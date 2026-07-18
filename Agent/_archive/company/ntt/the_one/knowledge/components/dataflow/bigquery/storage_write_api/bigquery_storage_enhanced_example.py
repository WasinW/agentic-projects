"""Enhanced BigQuery CDC Write — Option A: Read-Before-Write for Partial Column Updates.

Problem:
  CDC UPSERT replaces the ENTIRE row. If Topic A sends {A1, A2, B3} and Topic B
  sends {A1, B3, B4}, the second write overwrites A2 with NULL.

Solution:
  Before CDC write, query BQ for the existing row and merge non-null values
  from the new data with existing values, so no columns are lost.

Usage in pipeline (builder.py):
  # Before CDC write, add FillMissingColumnsDoFn
  enriched = (
      api_results
      | "ExtractPayload" >> beam.ParDo(ExtractCouponPayloadDoFn())
      | "FillMissing" >> beam.ParDo(
          FillMissingColumnsDoFn(
              project_id="the1-loyalty-data-prod",
              dataset="refined",
              table="coupons",
              primary_key_column="coupon_id",
              all_columns=ALL_REFINED_COLUMNS,
          )
      )
  )
  enriched | "WriteCDC" >> bq_cdc_sink

Based on: coupons-collector/src/adapters/output/bigquery_storage.py
"""

from __future__ import annotations

import logging
from typing import Any

import apache_beam as beam
from apache_beam.transforms import DoFn
from google.cloud import bigquery

logger = logging.getLogger(__name__)


# All columns in the refined table (excluding partition pseudo-columns)
# Update this list to match your actual table schema
ALL_REFINED_COLUMNS = [
    "member_id",
    "reward_id",
    "account_id",
    "coupon_id",
    "reward_type",
    "redemption_type",
    "status",
    # ... add all columns here
]


class FillMissingColumnsDoFn(DoFn):  # type: ignore[misc]
    """Query BQ for existing row and fill missing/null columns before CDC write.

    This prevents CDC UPSERT from overwriting existing non-null values with NULL
    when a Kafka topic only sends a subset of columns.

    Flow:
      1. Receive element dict with partial columns
      2. Identify which columns are missing or None
      3. If any missing, query BQ for the existing row by primary key
      4. Fill missing columns from existing row (COALESCE logic)
      5. Yield the complete row for CDC write

    Performance considerations:
      - Queries BQ once per element with missing columns (not every element)
      - Use batch lookups or caching for high-throughput scenarios
      - Consider SideInput with periodic refresh for frequently accessed data
    """

    def __init__(
        self,
        project_id: str,
        dataset: str,
        table: str,
        primary_key_column: str,
        all_columns: list[str],
    ) -> None:
        self._project_id = project_id
        self._dataset = dataset
        self._table = table
        self._pk_col = primary_key_column
        self._all_columns = all_columns
        self._client: bigquery.Client | None = None

    def setup(self) -> None:
        """Initialize BQ client (once per worker)."""
        self._client = bigquery.Client(project=self._project_id)

    def process(self, element: dict[str, Any]) -> list[dict[str, Any]]:
        """Fill missing columns from existing BQ row."""
        pk_value = element.get(self._pk_col)
        if not pk_value:
            # No primary key — can't look up existing row, pass through
            return [element]

        # Find columns that are missing or None
        missing_cols = [
            col for col in self._all_columns
            if col not in element or element[col] is None
        ]

        if not missing_cols:
            # All columns present — no need to query BQ
            return [element]

        # Query BQ for existing row (only missing columns)
        existing = self._fetch_existing_row(pk_value, missing_cols)

        if existing:
            # Fill missing columns from existing row
            for col in missing_cols:
                if col in existing and existing[col] is not None:
                    element[col] = existing[col]

        return [element]

    def _fetch_existing_row(
        self, pk_value: str, columns: list[str]
    ) -> dict[str, Any] | None:
        """Fetch specific columns from existing BQ row."""
        assert self._client is not None

        cols_str = ", ".join(columns)
        query = (
            f"SELECT {cols_str} "
            f"FROM `{self._project_id}.{self._dataset}.{self._table}` "
            f"WHERE {self._pk_col} = @pk_value "
            f"LIMIT 1"
        )

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("pk_value", "STRING", pk_value)
            ]
        )

        try:
            results = self._client.query(query, job_config=job_config).result()
            for row in results:
                return dict(row.items())
        except Exception as exc:
            logger.warning(
                "Failed to fetch existing row for %s=%s: %s",
                self._pk_col, pk_value, exc,
            )

        return None


# =============================================================================
# Option A-2: Batch version using SideInput (better for high throughput)
# =============================================================================


class FillMissingColumnsBatchDoFn(DoFn):  # type: ignore[misc]
    """Batch version: pre-load existing rows as SideInput.

    Better for high throughput — avoids per-element BQ queries.
    Trade-off: data might be slightly stale (loaded once at pipeline start
    or periodically via PeriodicImpulse).

    Usage:
      existing_rows = (
          p | "LoadExisting" >> beam.io.ReadFromBigQuery(
              query=f"SELECT * FROM `{project}.{dataset}.{table}`",
              use_standard_sql=True,
          )
          | "KeyByPK" >> beam.Map(lambda row: (row["coupon_id"], row))
      )
      existing_dict = beam.pvalue.AsDict(existing_rows)

      enriched = (
          new_rows
          | "FillMissing" >> beam.ParDo(
              FillMissingColumnsBatchDoFn(
                  primary_key_column="coupon_id",
                  all_columns=ALL_REFINED_COLUMNS,
              ),
              existing=existing_dict,
          )
      )
    """

    def __init__(
        self,
        primary_key_column: str,
        all_columns: list[str],
    ) -> None:
        self._pk_col = primary_key_column
        self._all_columns = all_columns

    def process(
        self,
        element: dict[str, Any],
        existing: dict[str, dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Fill missing columns from SideInput lookup."""
        if existing is None:
            return [element]

        pk_value = element.get(self._pk_col)
        if not pk_value:
            return [element]

        existing_row = existing.get(pk_value)
        if not existing_row:
            return [element]

        # Fill missing/null columns from existing row
        for col in self._all_columns:
            if (col not in element or element[col] is None) and existing_row.get(col) is not None:
                element[col] = existing_row[col]

        return [element]


# =============================================================================
# Option C: GroupByKey Merge (merge partial rows within window)
# =============================================================================


class MergePartialRowsFn(beam.CombineFn):  # type: ignore[misc]
    """Merge partial rows from multiple topics within a window.

    Given multiple partial dicts with the same primary key,
    merge them by taking the latest non-null value for each column.

    Usage:
      merged = (
          all_topic_rows
          | "KeyByPK" >> beam.Map(lambda row: (row["coupon_id"], row))
          | "GroupByPK" >> beam.GroupByKey()
          | "MergeRows" >> beam.MapTuple(
              lambda pk, rows: MergePartialRowsFn.merge(list(rows))
          )
      )
    """

    @staticmethod
    def merge(rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge list of partial row dicts, preferring non-null values."""
        merged: dict[str, Any] = {}
        for row in rows:
            for key, value in row.items():
                if value is not None:
                    merged[key] = value
        return merged
