"""BigQuery Storage Write API adapter.

Writes data to BigQuery using Storage Write API.
Supports append, CDC (upsert), and batch modes.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import apache_beam as beam
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.transforms import DoFn, ParDo
from apache_beam.utils.timestamp import Timestamp

logger = logging.getLogger(__name__)


def _convert_field_for_beam(field: dict[str, Any]) -> dict[str, Any]:
    """Convert a single BQ schema field for Beam compatibility.

    - DATETIME → STRING (Beam cannot map DATETIME to a Python type;
      values are already ISO strings, BQ parses them into DATETIME columns)
    - RECORD with nested fields: recurse into sub-fields
    """
    result = dict(field)  # shallow copy
    if result.get("type", "").upper() == "DATETIME":
        result["type"] = "STRING"
    if result.get("type", "").upper() == "RECORD" and "fields" in result:
        result["fields"] = [_convert_field_for_beam(f) for f in result["fields"]]
    return result


def _convert_schema_for_beam(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert BQ schema for Beam Storage Write API compatibility.

    Recursively converts DATETIME→STRING while preserving REPEATED RECORD
    structure (mode, nested fields) needed for correct proto generation.
    """
    return {"fields": [_convert_field_for_beam(f) for f in schema["fields"]]}


class _LogFailedRowsDoFn(DoFn):  # type: ignore[misc]
    """Log failed rows from BigQuery Storage Write API."""

    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._error_count = 0

    def process(self, element: Any) -> None:
        """Log each failed row."""
        self._error_count += 1
        # element is a tuple of (row, error_message) or similar structure
        logger.error(
            "BigQuery write failed for table=%s: row=%s",
            self._table_name,
            element,
        )


def write_to_bigquery_append(
    pcoll: beam.PCollection[Any],
    table: str,
    schema: dict[str, Any],
    partition_field: str | None = None,
    step_name: str = "WriteToBigQueryAppend",
    triggering_frequency: int = 60,
    num_storage_api_streams: int | None = None,
    with_auto_sharding: bool = True,
) -> None:
    """Write to BigQuery using Storage Write API (append mode).

    Args:
        pcoll: Input PCollection of dicts
        table: Full table reference (project:dataset.table)
        schema: BigQuery schema dict
        partition_field: Column name for time partitioning (DAY)
        step_name: Beam step name prefix
        triggering_frequency: Batch trigger frequency in seconds
        num_storage_api_streams: Number of Storage API streams (optional)
        with_auto_sharding: Enable auto-sharding for better parallelism (default True)
    """
    if pcoll is None:
        raise ValueError("pcoll must not be None")
    if not table:
        raise ValueError("table must be provided")

    additional_params: dict[str, Any] = {}
    if partition_field:
        additional_params["timePartitioning"] = {
            "type": "DAY",
            "field": partition_field,
        }

    logger.info(
        "Writing to BigQuery (append): table=%s partition_field=%s triggering_frequency=%ds auto_sharding=%s",
        table,
        partition_field,
        triggering_frequency,
        with_auto_sharding,
    )

    # Convert DATETIME→STRING for Beam compatibility (values are already ISO strings)
    beam_schema = _convert_schema_for_beam(schema)

    # Build WriteToBigQuery with proper configuration for streaming
    write_result = pcoll | f"{step_name}" >> WriteToBigQuery(
        table=table,
        schema=beam_schema,
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        additional_bq_parameters=additional_params if additional_params else None,
        triggering_frequency=triggering_frequency,
        with_auto_sharding=with_auto_sharding,
        num_storage_api_streams=num_storage_api_streams,
    )

    # Log failed rows for debugging - this is critical for diagnosing issues
    # Storage Write API returns failed rows via FAILED_ROWS output
    _ = write_result.failed_rows_with_errors | f"{step_name}_LogFailedRows" >> ParDo(_LogFailedRowsDoFn(table))


class _WrapCdcRowDoFn(DoFn):  # type: ignore[misc]
    """Wrap plain data dicts into CDC dict format for BigQuery Storage Write API.

    CDC writes require rows with:
    - row_mutation_info: dict with mutation_type and change_sequence_number
    - record: dict with actual data fields (Timestamp values converted to string)

    Follows the working pattern from insight/customer-profile-pipeline:
    - Timestamp objects MUST be converted to ISO strings for CDC compatibility
    - change_sequence_number uses microsecond timestamp for ordering
    """

    def process(self, element: dict[str, Any]) -> list[dict[str, Any]]:
        """Wrap element in CDC dict structure with sanitized values."""
        # Pop _is_delete flag before building record (not a BQ column)
        is_delete = element.pop("_is_delete", False)
        mutation_type = "DELETE" if is_delete else "UPSERT"

        # Sanitize record: convert Beam Timestamp → ISO string with Z suffix
        # Storage Write API CDC cannot handle Timestamp objects in nested RECORD.
        # Z suffix required because Java Instant.parse() needs timezone indicator.
        record: dict[str, Any] = {}
        for key, value in element.items():
            if isinstance(value, Timestamp):
                record[key] = value.to_utc_datetime().strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                record[key] = value

        # Sequence number: microsecond timestamp for ordering
        seq_num = str(int(time.time() * 1_000_000))

        return [
            {
                "row_mutation_info": {
                    "mutation_type": mutation_type,
                    "change_sequence_number": seq_num,
                },
                "record": record,
            }
        ]


def _wrap_schema_for_cdc(schema: dict[str, Any]) -> dict[str, Any]:
    """Wrap a BigQuery schema dict with CDC RECORD fields.

    CDC writes via Storage Write API require rows wrapped in:
    - row_mutation_info (RECORD: mutation_type, change_sequence_number)
    - record (RECORD: actual data fields)

    TIMESTAMP fields are converted to STRING in the CDC schema because
    Storage Write API CDC cannot serialize Timestamp in nested RECORD
    across the Python→Java cross-language boundary.

    Follows the working pattern from insight/customer-profile-pipeline.
    """
    # Convert record fields: TIMESTAMP/DATETIME → STRING, preserve mode + nested fields
    temporal_types = {"TIMESTAMP", "DATE", "DATETIME", "TIME"}
    cdc_record_fields = []
    for field in schema["fields"]:
        field_type = field.get("type", "").upper()
        cdc_field: dict[str, Any] = {
            "name": field["name"],
            "type": "STRING" if field_type in temporal_types else field.get("type", ""),
            "mode": field.get("mode", "NULLABLE"),
        }
        if field_type == "RECORD" and "fields" in field:
            cdc_field["fields"] = field["fields"]
        cdc_record_fields.append(cdc_field)

    return {
        "fields": [
            {
                "name": "row_mutation_info",
                "type": "RECORD",
                "mode": "NULLABLE",
                "fields": [
                    {"name": "mutation_type", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "change_sequence_number", "type": "STRING", "mode": "REQUIRED"},
                ],
            },
            {
                "name": "record",
                "type": "RECORD",
                "mode": "NULLABLE",
                "fields": cdc_record_fields,
            },
        ]
    }


def write_to_bigquery_cdc(
    pcoll: beam.PCollection[Any],
    table: str,
    schema: dict[str, Any],
    primary_key: list[str],
    step_name: str = "WriteToBigQueryCDC",
    triggering_frequency: int = 60,
    with_auto_sharding: bool = True,
) -> None:
    """Write to BigQuery using Storage Write API with CDC (upsert mode).

    Wraps plain data rows into CDC dict format (row_mutation_info + record)
    with TIMESTAMP→STRING conversion, matching the working pattern from
    insight/customer-profile-pipeline.

    The target table MUST already exist with PRIMARY KEY and max_staleness.

    Args:
        pcoll: Input PCollection of dicts (plain data rows)
        table: Full table reference (project:dataset.table)
        schema: BigQuery schema dict for the record fields
        primary_key: List of column names for primary key
        step_name: Beam step name prefix
        triggering_frequency: Batch trigger frequency in seconds
        with_auto_sharding: Enable auto-sharding for better parallelism (default True)
    """
    if pcoll is None:
        raise ValueError("pcoll must not be None")
    if not table:
        raise ValueError("table must be provided")
    if not primary_key:
        raise ValueError("primary_key must be provided for CDC mode")

    logger.info(
        "Writing to BigQuery (CDC): table=%s primary_key=%s triggering_frequency=%ds auto_sharding=%s",
        table,
        primary_key,
        triggering_frequency,
        with_auto_sharding,
    )

    # Wrap plain data dicts into CDC dict format
    cdc_rows = pcoll | f"{step_name}_WrapCDC" >> ParDo(_WrapCdcRowDoFn())

    # Wrap schema with CDC STRUCT fields (row_mutation_info + record)
    cdc_schema = _wrap_schema_for_cdc(schema)

    # Table must already exist with PRIMARY KEY + max_staleness (CREATE_NEVER).
    # Schema is explicit (not inferred) — WriteToBigQuery converts dicts to
    # beam.Row internally via ConvertToBeamRows + beam_row_from_dict.
    write_result = cdc_rows | f"{step_name}" >> WriteToBigQuery(
        table=table,
        schema=cdc_schema,
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
        triggering_frequency=triggering_frequency,
        with_auto_sharding=with_auto_sharding,
        use_cdc_writes=True,
        use_at_least_once=True,
        primary_key=primary_key,
    )

    # Log failed rows for debugging
    _ = write_result.failed_rows_with_errors | f"{step_name}_LogFailedRows" >> ParDo(_LogFailedRowsDoFn(table))


def write_to_bigquery_batch(
    pcoll: beam.PCollection[Any],
    table: str,
    schema: dict[str, Any],
    partition_field: str | None = None,
    write_disposition: str = "WRITE_APPEND",
    step_name: str = "WriteToBigQueryBatch",
) -> None:
    """Write to BigQuery using Storage Write API (batch mode - no streaming triggers).

    Args:
        pcoll: Input PCollection of dicts
        table: Full table reference (project:dataset.table)
        schema: BigQuery schema dict
        partition_field: Column name for time partitioning (DAY)
        write_disposition: WRITE_APPEND or WRITE_TRUNCATE
        step_name: Beam step name prefix
    """
    if pcoll is None:
        raise ValueError("pcoll must not be None")
    if not table:
        raise ValueError("table must be provided")

    bq_disposition = (
        beam.io.BigQueryDisposition.WRITE_TRUNCATE
        if write_disposition == "WRITE_TRUNCATE"
        else beam.io.BigQueryDisposition.WRITE_APPEND
    )

    additional_params: dict[str, Any] = {}
    if partition_field:
        additional_params["timePartitioning"] = {
            "type": "DAY",
            "field": partition_field,
        }

    logger.info(
        "Writing to BigQuery (batch): table=%s partition_field=%s disposition=%s",
        table,
        partition_field,
        write_disposition,
    )

    # Convert DATETIME→STRING for Beam compatibility (values are already ISO strings)
    beam_schema = _convert_schema_for_beam(schema)

    # Batch mode: no triggering_frequency, no auto_sharding
    write_result = pcoll | f"{step_name}" >> WriteToBigQuery(
        table=table,
        schema=beam_schema,
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        write_disposition=bq_disposition,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        additional_bq_parameters=additional_params if additional_params else None,
    )

    # Log failed rows for debugging
    _ = write_result.failed_rows_with_errors | f"{step_name}_LogFailedRows" >> ParDo(_LogFailedRowsDoFn(table))
