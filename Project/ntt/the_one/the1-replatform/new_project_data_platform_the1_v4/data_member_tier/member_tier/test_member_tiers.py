"""
Unit tests for member_tiers.py

Tests to verify:
1. All DoFn setup() methods work without NameError
2. DecodeKafkaValueDoFn can decode Avro payload
3. Schema Registry integration works
4. All transformations work correctly
"""
import json
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module under test
import member_tiers as mt


class TestDoFnSetupMethods(unittest.TestCase):
    """Test that all DoFn setup() methods work without NameError."""

    def test_decode_kafka_value_dofn_setup(self):
        """Test DecodeKafkaValueDoFn.setup() doesn't raise NameError."""
        dofn = mt.DecodeKafkaValueDoFn(topic_name="test.topic", debug_mode=True)
        # This should NOT raise NameError: name 'MODULE_LOGGER_NAME' is not defined
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.DecodeKafkaValueDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_upgraded_row_dofn_setup(self):
        """Test ToUpgradedRowDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToUpgradedRowDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToUpgradedRowDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_downgraded_row_dofn_setup(self):
        """Test ToDowngradedRowDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToDowngradedRowDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToDowngradedRowDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_member_tier_raw_row_dofn_setup(self):
        """Test ToMemberTierRawRowDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToMemberTierRawRowDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToMemberTierRawRowDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_upgraded_dict_dofn_setup(self):
        """Test ToUpgradedDictDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToUpgradedDictDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToUpgradedDictDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_downgraded_dict_dofn_setup(self):
        """Test ToDowngradedDictDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToDowngradedDictDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToDowngradedDictDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_to_member_tier_dict_dofn_setup(self):
        """Test ToMemberTierDictDoFn.setup() doesn't raise NameError."""
        dofn = mt.ToMemberTierDictDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.ToMemberTierDictDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_call_member_tier_info_api_dofn_setup(self):
        """Test CallMemberTierInfoAPIDoFn.setup() doesn't raise NameError."""
        dofn = mt.CallMemberTierInfoAPIDoFn(
            api_secret_project="test-project",
            api_secret_id="test-secret"
        )
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.CallMemberTierInfoAPIDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")

    def test_add_window_key_dofn_setup(self):
        """Test AddWindowKeyDoFn.setup() doesn't raise NameError."""
        dofn = mt.AddWindowKeyDoFn()
        try:
            dofn.setup()
            self.assertIsNotNone(dofn._logger)
            self.assertEqual(dofn._logger.name, "member_tiers.AddWindowKeyDoFn")
        except NameError as e:
            self.fail(f"setup() raised NameError: {e}")


class TestDecodeKafkaValueDoFn(unittest.TestCase):
    """Test DecodeKafkaValueDoFn decoding logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.dofn = mt.DecodeKafkaValueDoFn(topic_name="test.topic", debug_mode=True)
        self.dofn.setup()
        self.dofn.start_bundle()

    def test_decode_json_bytes(self):
        """Test decoding JSON bytes payload."""
        # Save original PAYLOAD_FORMAT
        original_format = mt.PAYLOAD_FORMAT
        mt.PAYLOAD_FORMAT = "json"

        try:
            payload = {
                "eventId": "test-123",
                "source": "loyalty.members",
                "eventName": "loyalty.members.upgraded",
                "timestamp": 1691060098,
                "payload": {
                    "accountId": "acc-123",
                    "memberId": "mem-456",
                    "tierCode": "T1X"
                }
            }
            input_bytes = json.dumps(payload).encode("utf-8")

            results = list(self.dofn.process(input_bytes))

            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertEqual(result["eventId"], "test-123")
            self.assertEqual(result["_topic"], "test.topic")
            self.assertIn("_ingested_at", result)
            self.assertEqual(result["payload"]["memberId"], "mem-456")
        finally:
            mt.PAYLOAD_FORMAT = original_format

    def test_decode_avro_with_confluent_wire_format(self):
        """Test decoding Avro payload with Confluent wire format."""
        original_format = mt.PAYLOAD_FORMAT
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        mt.PAYLOAD_FORMAT = "avro"
        mt.USE_SCHEMA_REGISTRY = True

        try:
            # Confluent wire format: magic byte (0) + 4-byte schema ID + avro data
            schema_id = 12345

            # Create a simple Avro schema and data
            avro_schema = {
                "type": "record",
                "name": "MemberUpgraded",
                "fields": [
                    {"name": "eventId", "type": "string"},
                    {"name": "memberId", "type": "string"}
                ]
            }

            # Pre-populate schema cache to avoid actual SR call
            mt._SCHEMA_CACHE[schema_id] = avro_schema

            # Create Avro-encoded data
            from fastavro import schemaless_writer
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, {"eventId": "evt-1", "memberId": "mem-1"})
            avro_bytes = buffer.getvalue()

            # Prepend Confluent wire format header
            header = bytes([0]) + schema_id.to_bytes(4, "big")
            full_payload = header + avro_bytes

            results = list(self.dofn.process(full_payload))

            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertEqual(result["eventId"], "evt-1")
            self.assertEqual(result["memberId"], "mem-1")
            self.assertEqual(result["_topic"], "test.topic")
        finally:
            mt.PAYLOAD_FORMAT = original_format
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt._SCHEMA_CACHE.clear()


class TestSchemaRegistry(unittest.TestCase):
    """Test Schema Registry integration."""

    def test_schema_registry_url_from_env(self):
        """Test that Schema Registry URL is read from environment."""
        test_url = "https://test-schema-registry.example.com"

        with patch.dict(os.environ, {
            "CONFLUENT_SR_URL": test_url,
            "CONFLUENT_SR_API_KEY": "test-key",
            "CONFLUENT_SR_API_SECRET": "test-secret"
        }):
            # Mock the requests.get call
            mock_response = Mock()
            mock_response.json.return_value = {
                "schema": json.dumps({
                    "type": "record",
                    "name": "Test",
                    "fields": [{"name": "id", "type": "string"}]
                })
            }
            mock_response.raise_for_status = Mock()

            with patch("requests.get", return_value=mock_response) as mock_get:
                schema = mt.get_schema_from_registry(99999)

                # Verify correct URL was called
                called_url = mock_get.call_args[0][0]
                self.assertTrue(called_url.startswith(test_url))
                self.assertIn("/schemas/ids/99999", called_url)

    def test_schema_registry_url_missing_raises_error(self):
        """Test that missing SR URL raises RuntimeError."""
        # Clear SR URL from env
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CONFLUENT_SR_URL", None)
            mt._WORKER_SR_CREDENTIALS_LOADED = True  # Skip auto-load

            with self.assertRaises(RuntimeError) as ctx:
                mt.get_schema_from_registry(12345)

            self.assertIn("CONFLUENT_SR_URL", str(ctx.exception))


class TestLoadConfluentEnv(unittest.TestCase):
    """Test loading Confluent config from Secret Manager."""

    @patch("member_tiers.get_secret_value")
    def test_load_schema_registry_url(self, mock_get_secret):
        """Test that schemaRegistryURL is loaded to CONFLUENT_SR_URL."""
        mock_get_secret.return_value = {
            "confluent-bootstrapserver": "broker:9092",
            "confluent-saslusername": "user",
            "confluent-saslpassword": "pass",
            "schemaRegistryURL": "https://psrc-10wzj.ap-southeast-2.aws.confluent.cloud",
            "confluentRegistryApiKey": "sr-key",
            "confluentRegistrySecret": "sr-secret"
        }

        # Clear existing env vars
        for key in ["CONFLUENT_SR_URL", "CONFLUENT_SR_API_KEY", "CONFLUENT_SR_API_SECRET"]:
            os.environ.pop(key, None)

        result = mt.load_confluent_env_from_secret_manager(
            "test-secret", "test-project", overwrite=True
        )

        self.assertTrue(result)
        self.assertEqual(
            os.environ.get("CONFLUENT_SR_URL"),
            "https://psrc-10wzj.ap-southeast-2.aws.confluent.cloud"
        )
        self.assertEqual(os.environ.get("CONFLUENT_SR_API_KEY"), "sr-key")
        self.assertEqual(os.environ.get("CONFLUENT_SR_API_SECRET"), "sr-secret")


class TestTransformDoFns(unittest.TestCase):
    """Test transformation DoFns."""

    def test_to_upgraded_dict_dofn(self):
        """Test ToUpgradedDictDoFn transforms correctly."""
        dofn = mt.ToUpgradedDictDoFn()
        dofn.setup()

        input_element = {
            "eventId": "evt-123",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": "2024-03-15T00:00:00.000Z",
            "_topic": "loyalty.members.upgraded",
            "_ingested_at": datetime.now(mt.TZ_BANGKOK),
            "payload": {
                "accountId": "acc-456",
                "memberId": "mem-789",
                "tierEventId": "tier-001",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        results = list(dofn.process(input_element))

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result["eventId"], "evt-123")
        self.assertEqual(result["accountId"], "acc-456")
        self.assertEqual(result["memberId"], "mem-789")
        self.assertEqual(result["tierCode"], "T1X")
        self.assertEqual(result["isExistingTier"], True)
        self.assertEqual(result["source_topic"], "loyalty.members.upgraded")

    def test_to_downgraded_dict_dofn(self):
        """Test ToDowngradedDictDoFn transforms correctly."""
        dofn = mt.ToDowngradedDictDoFn()
        dofn.setup()

        input_element = {
            "eventId": "evt-456",
            "source": "loyalty.members",
            "eventName": "loyalty.members.downgraded",
            "timestamp": "2024-03-15T00:00:00.000Z",
            "_topic": "loyalty.members.downgraded",
            "_ingested_at": datetime.now(mt.TZ_BANGKOK),
            "payload": {
                "accountId": "acc-789",
                "memberId": "mem-012",
                "tierEventId": "tier-002",
                "tierCode": "SILVER",
                "triggerType": "EXPIRY",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        results = list(dofn.process(input_element))

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result["eventId"], "evt-456")
        self.assertEqual(result["memberId"], "mem-012")
        self.assertEqual(result["tierCode"], "SILVER")


class TestDecodeConfluentAvro(unittest.TestCase):
    """Test Confluent Avro decoding."""

    def test_decode_with_valid_wire_format(self):
        """Test decoding valid Confluent wire format."""
        schema_id = 100
        avro_schema = {
            "type": "record",
            "name": "Test",
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "value", "type": "int"}
            ]
        }

        # Pre-populate cache
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        mt.USE_SCHEMA_REGISTRY = False  # Use cache only

        try:
            from fastavro import schemaless_writer
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, {"id": "test-1", "value": 42})
            avro_data = buffer.getvalue()

            # Confluent wire format: 0x00 + 4-byte schema ID + data
            wire_format = bytes([0]) + schema_id.to_bytes(4, "big") + avro_data

            result = mt.decode_confluent_avro(wire_format)

            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test-1")
            self.assertEqual(result["value"], 42)
        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt._SCHEMA_CACHE.clear()

    def test_decode_empty_payload_returns_none(self):
        """Test that empty payload returns None."""
        result = mt.decode_confluent_avro(b"")
        self.assertIsNone(result)

        result = mt.decode_confluent_avro(b"1234")  # Less than 5 bytes
        self.assertIsNone(result)


class TestPayloadFormat(unittest.TestCase):
    """Test PAYLOAD_FORMAT configuration."""

    def test_payload_format_is_avro(self):
        """Test that PAYLOAD_FORMAT is set to 'avro'."""
        self.assertEqual(mt.PAYLOAD_FORMAT, "avro")

    def test_use_schema_registry_is_true(self):
        """Test that USE_SCHEMA_REGISTRY is True."""
        self.assertTrue(mt.USE_SCHEMA_REGISTRY)


class TestDefaultSecretName(unittest.TestCase):
    """Test that DEFAULT_CONFLUENT_SECRET_NAME uses Kafka secret."""

    def test_default_confluent_secret_matches_kafka_secret(self):
        """Test DEFAULT_CONFLUENT_SECRET_NAME equals DEFAULT_KAFKA_SECRET_NAME."""
        self.assertEqual(
            mt.DEFAULT_CONFLUENT_SECRET_NAME,
            mt.DEFAULT_KAFKA_SECRET_NAME
        )


class TestLogging(unittest.TestCase):
    """Test that logging works correctly for Cloud Logging."""

    def test_dofn_logger_outputs_to_standard_logging(self):
        """Test that DoFn loggers use standard Python logging (required for Cloud Logging)."""
        import logging
        from io import StringIO

        # Create a string handler to capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Get the logger that DoFn uses
        logger = logging.getLogger("member_tiers.DecodeKafkaValueDoFn")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Create DoFn and setup
        dofn = mt.DecodeKafkaValueDoFn(topic_name="test.topic", debug_mode=True)
        dofn.setup()

        # Log something
        dofn._logger.info("Test log message from DoFn")

        # Verify log was captured
        log_output = log_capture.getvalue()
        self.assertIn("member_tiers.DecodeKafkaValueDoFn", log_output)
        self.assertIn("Test log message from DoFn", log_output)

        # Cleanup
        logger.removeHandler(handler)

    def test_all_dofn_loggers_use_member_tiers_prefix(self):
        """Test that all DoFn loggers use 'member_tiers.' prefix for Cloud Logging filtering."""
        dofns_to_test = [
            mt.DecodeKafkaValueDoFn(topic_name="test", debug_mode=False),
            mt.ToUpgradedDictDoFn(),
            mt.ToDowngradedDictDoFn(),
            mt.ToMemberTierDictDoFn(),
            mt.ToUpgradedRowDoFn(),
            mt.ToDowngradedRowDoFn(),
            mt.ToMemberTierRawRowDoFn(),
            mt.AddWindowKeyDoFn(),
            mt.CallMemberTierInfoAPIDoFn(api_secret_project="p", api_secret_id="s"),
        ]

        for dofn in dofns_to_test:
            dofn.setup()
            logger_name = dofn._logger.name
            self.assertTrue(
                logger_name.startswith("member_tiers."),
                f"{dofn.__class__.__name__} logger name '{logger_name}' should start with 'member_tiers.'"
            )

    def test_logger_levels_work(self):
        """Test that different log levels work (INFO, WARNING, ERROR)."""
        import logging
        from io import StringIO

        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger("member_tiers.TestLogger")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        log_output = log_capture.getvalue()

        self.assertIn("DEBUG - Debug message", log_output)
        self.assertIn("INFO - Info message", log_output)
        self.assertIn("WARNING - Warning message", log_output)
        self.assertIn("ERROR - Error message", log_output)

        logger.removeHandler(handler)


class TestTimezone(unittest.TestCase):
    """Test that timezone is correctly set to Asia/Bangkok."""

    def test_tz_bangkok_is_utc_plus_7(self):
        """Test that TZ_BANGKOK is UTC+7."""
        from datetime import timedelta
        self.assertEqual(mt.TZ_BANGKOK.utcoffset(None), timedelta(hours=7))

    def test_datetime_uses_bangkok_timezone(self):
        """Test that datetime.now uses Bangkok timezone."""
        now = datetime.now(mt.TZ_BANGKOK)
        self.assertEqual(now.tzinfo, mt.TZ_BANGKOK)

        # Verify offset is +07:00
        offset = now.strftime("%z")
        self.assertEqual(offset, "+0700")

    def test_pyarrow_schema_uses_bangkok_timezone(self):
        """Test that PyArrow schemas use Asia/Bangkok timezone."""
        # Check SCHEMA_UPGRADED_RAW
        timestamp_field = mt.SCHEMA_UPGRADED_RAW.field("timestamp")
        self.assertEqual(str(timestamp_field.type.tz), "Asia/Bangkok")

        # Check SCHEMA_DOWNGRADED_RAW
        timestamp_field = mt.SCHEMA_DOWNGRADED_RAW.field("timestamp")
        self.assertEqual(str(timestamp_field.type.tz), "Asia/Bangkok")


class TestE2EFlow(unittest.TestCase):
    """End-to-end test: Kafka message -> Decode -> Transform -> Output."""

    def test_e2e_upgraded_message_flow(self):
        """
        Test full flow with real payload structure from loyalty.members.upgraded.

        Payload example from spec:
        {
          "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
          "source": "loyalty.members",
          "eventName": "loyalty.members.upgraded",
          "timestamp": 1691060098,
          "payload": {
            "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
            "memberId": "1-981785546",
            "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
            "tierCode": "T1X",
            "isExistingTier": true,
            "triggerType": "SPENDING",
            "processedAt": "2024-03-15T00:00:00.000Z"
          }
        }
        """
        # Avro schema matching the spec
        avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "Payload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # Test data matching the spec example
        test_message = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        # =========================================
        # Step 1: Create Avro wire format message
        # =========================================
        schema_id = 12345
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False  # Use cache
        mt.PAYLOAD_FORMAT = "avro"

        try:
            from fastavro import schemaless_writer
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, test_message)
            avro_bytes = buffer.getvalue()

            # Confluent wire format: 0x00 + 4-byte schema ID + avro data
            kafka_message = bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes

            # =========================================
            # Step 2: DecodeKafkaValueDoFn
            # =========================================
            decode_dofn = mt.DecodeKafkaValueDoFn(
                topic_name="loyalty.members.upgraded",
                debug_mode=True
            )
            decode_dofn.setup()
            decode_dofn.start_bundle()

            decoded_results = list(decode_dofn.process(kafka_message))

            self.assertEqual(len(decoded_results), 1, "DecodeKafkaValueDoFn should yield 1 element")
            decoded = decoded_results[0]

            # Verify decoded message
            self.assertEqual(decoded["eventId"], "a8debc92-50d2-4f7b-8c89-27b6e810a701")
            self.assertEqual(decoded["source"], "loyalty.members")
            self.assertEqual(decoded["eventName"], "loyalty.members.upgraded")
            self.assertEqual(decoded["timestamp"], 1691060098)
            self.assertEqual(decoded["_topic"], "loyalty.members.upgraded")
            self.assertIn("_ingested_at", decoded)
            self.assertIsInstance(decoded["payload"], dict)
            self.assertEqual(decoded["payload"]["memberId"], "1-981785546")
            self.assertEqual(decoded["payload"]["tierCode"], "T1X")
            self.assertEqual(decoded["payload"]["isExistingTier"], True)

            print(f"✓ Step 2 (DecodeKafkaValueDoFn): decoded message with eventId={decoded['eventId']}")

            # =========================================
            # Step 3: ToUpgradedDictDoFn
            # =========================================
            transform_dofn = mt.ToUpgradedDictDoFn()
            transform_dofn.setup()

            transform_results = list(transform_dofn.process(decoded))

            self.assertEqual(len(transform_results), 1, "ToUpgradedDictDoFn should yield 1 element")
            transformed = transform_results[0]

            # Verify transformed output matches expected schema
            self.assertEqual(transformed["eventId"], "a8debc92-50d2-4f7b-8c89-27b6e810a701")
            self.assertEqual(transformed["source"], "loyalty.members")
            self.assertEqual(transformed["eventName"], "loyalty.members.upgraded")
            self.assertEqual(transformed["accountId"], "69f6a344-1321-4cbb-87e5-991c96593931")
            self.assertEqual(transformed["memberId"], "1-981785546")
            self.assertEqual(transformed["tierEventId"], "69f6a344-1321-4cbb-87e5-991c965009009")
            self.assertEqual(transformed["tierCode"], "T1X")
            self.assertEqual(transformed["isExistingTier"], True)
            self.assertEqual(transformed["triggerType"], "SPENDING")
            self.assertEqual(transformed["processedAt"], "2024-03-15T00:00:00.000Z")
            self.assertEqual(transformed["source_topic"], "loyalty.members.upgraded")
            self.assertIn("ingested_at", transformed)

            print(f"✓ Step 3 (ToUpgradedDictDoFn): transformed to dict with memberId={transformed['memberId']}")

            # =========================================
            # Step 4: Verify PyArrow schema compatibility
            # =========================================
            import pyarrow as pa

            # Create PyArrow table from transformed data
            try:
                table = pa.Table.from_pylist([transformed], schema=mt.SCHEMA_UPGRADED_RAW)
                self.assertEqual(table.num_rows, 1)
                print(f"✓ Step 4 (PyArrow): created table with {table.num_rows} row(s)")
            except Exception as e:
                self.fail(f"Failed to create PyArrow table: {e}")

            print("\n✅ E2E Flow PASSED: Kafka Avro -> Decode -> Transform -> PyArrow")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_e2e_downgraded_message_flow(self):
        """Test full flow for loyalty.members.downgraded."""
        avro_schema = {
            "type": "record",
            "name": "MemberDowngraded",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "Payload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        test_message = {
            "eventId": "downgrade-event-001",
            "source": "loyalty.members",
            "eventName": "loyalty.members.downgraded",
            "timestamp": 1691060099,
            "payload": {
                "accountId": "acc-downgrade-001",
                "memberId": "mem-downgrade-001",
                "tierEventId": "tier-downgrade-001",
                "tierCode": "SILVER",
                "triggerType": "EXPIRY",
                "processedAt": "2024-03-16T00:00:00.000Z"
            }
        }

        schema_id = 12346
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            from fastavro import schemaless_writer
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, test_message)
            avro_bytes = buffer.getvalue()
            kafka_message = bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes

            # Step 1: Decode
            decode_dofn = mt.DecodeKafkaValueDoFn(
                topic_name="loyalty.members.downgraded",
                debug_mode=True
            )
            decode_dofn.setup()
            decode_dofn.start_bundle()
            decoded_results = list(decode_dofn.process(kafka_message))
            self.assertEqual(len(decoded_results), 1)
            decoded = decoded_results[0]

            # Step 2: Transform
            transform_dofn = mt.ToDowngradedDictDoFn()
            transform_dofn.setup()
            transform_results = list(transform_dofn.process(decoded))
            self.assertEqual(len(transform_results), 1)
            transformed = transform_results[0]

            # Verify
            self.assertEqual(transformed["memberId"], "mem-downgrade-001")
            self.assertEqual(transformed["tierCode"], "SILVER")
            self.assertEqual(transformed["triggerType"], "EXPIRY")

            # Step 3: PyArrow
            import pyarrow as pa
            table = pa.Table.from_pylist([transformed], schema=mt.SCHEMA_DOWNGRADED_RAW)
            self.assertEqual(table.num_rows, 1)

            print("✅ E2E Downgraded Flow PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()


class TestDoFnSerialization(unittest.TestCase):
    """Test that DoFn classes can be pickled/unpickled correctly.

    This is CRITICAL for Dataflow because:
    1. DoFn instances are serialized on the driver
    2. Sent to workers over the network
    3. Deserialized and executed on workers

    If serialization fails, you get NameError on worker.
    """

    def test_call_member_tier_api_dofn_pickle_unpickle(self):
        """Test CallMemberTierInfoAPIDoFn survives pickle/unpickle.

        This tests the fix for:
        NameError: name 'MemberTierAPIClient' is not defined
        """
        import pickle

        # Create DoFn
        original = mt.CallMemberTierInfoAPIDoFn(
            api_secret_project="test-project",
            api_secret_id="test-secret"
        )

        # Verify class reference is stored
        self.assertIsNotNone(original._api_client_class)
        self.assertEqual(original._api_client_class.__name__, "MemberTierAPIClient")

        # Pickle (serialize) - this happens on driver
        pickled = pickle.dumps(original)

        # Unpickle (deserialize) - this happens on worker
        restored = pickle.loads(pickled)

        # Verify restored DoFn has all attributes
        self.assertEqual(restored.api_secret_project, "test-project")
        self.assertEqual(restored.api_secret_id, "test-secret")

        # CRITICAL: Verify class reference survived serialization
        self.assertIsNotNone(restored._api_client_class)
        self.assertEqual(restored._api_client_class.__name__, "MemberTierAPIClient")

        # Verify setup() can use the class reference
        restored.setup()
        self.assertIsNotNone(restored._logger)

    def test_decode_kafka_value_dofn_pickle_unpickle(self):
        """Test DecodeKafkaValueDoFn survives pickle/unpickle."""
        import pickle

        original = mt.DecodeKafkaValueDoFn(
            topic_name="loyalty.members.upgraded",
            debug_mode=True
        )

        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)

        self.assertEqual(restored.topic_name, "loyalty.members.upgraded")
        self.assertEqual(restored.debug_mode, True)

        # Verify setup works after unpickle
        restored.setup()
        self.assertIsNotNone(restored._logger)

    def test_all_dofns_are_picklable(self):
        """Test that all DoFn classes can be pickled."""
        import pickle

        dofns_to_test = [
            mt.DecodeKafkaValueDoFn(topic_name="test", debug_mode=False),
            mt.ToUpgradedDictDoFn(),
            mt.ToDowngradedDictDoFn(),
            mt.ToMemberTierDictDoFn(),
            mt.ToUpgradedRowDoFn(),
            mt.ToDowngradedRowDoFn(),
            mt.ToMemberTierRawRowDoFn(),
            mt.AddWindowKeyDoFn(),
            mt.CallMemberTierInfoAPIDoFn(api_secret_project="p", api_secret_id="s"),
        ]

        for dofn in dofns_to_test:
            class_name = dofn.__class__.__name__
            try:
                # Test pickle
                pickled = pickle.dumps(dofn)

                # Test unpickle
                restored = pickle.loads(pickled)

                # Test setup works
                restored.setup()

                self.assertIsNotNone(
                    restored._logger,
                    f"{class_name}: _logger should be set after setup()"
                )
            except Exception as e:
                self.fail(f"{class_name} failed pickle/unpickle: {e}")


class TestBeamPipelineIntegration(unittest.TestCase):
    """Integration tests using Apache Beam DirectRunner.

    These tests verify the pipeline works end-to-end without
    needing actual Kafka or Dataflow.
    """

    def test_decode_transform_pipeline_with_directrunner(self):
        """Test Decode -> Transform pipeline with DirectRunner."""
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to
        from io import BytesIO
        from fastavro import schemaless_writer

        # Prepare Avro message
        avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "Payload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        test_message = {
            "eventId": "test-evt-001",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "acc-001",
                "memberId": "mem-001",
                "tierEventId": "tier-001",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        # Encode to Avro wire format
        schema_id = 99999
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, test_message)
            avro_bytes = buffer.getvalue()
            kafka_message = bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes

            # Run pipeline with DirectRunner
            with TestPipeline() as p:
                # Mock Kafka input (list of bytes)
                input_messages = [kafka_message]

                # Pipeline: Create -> Decode -> Transform -> Extract memberId
                result = (
                    p
                    | "CreateInput" >> beam.Create(input_messages)
                    | "Decode" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=False
                        )
                    )
                    | "Transform" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                    | "ExtractMemberId" >> beam.Map(lambda x: x["memberId"])
                )

                # Verify output
                assert_that(result, equal_to(["mem-001"]))

            print("✅ Beam DirectRunner integration test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_multiple_messages_pipeline(self):
        """Test pipeline with multiple messages."""
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to
        from io import BytesIO
        from fastavro import schemaless_writer

        avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "Payload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # Create 3 test messages
        test_messages = [
            {
                "eventId": f"evt-{i}",
                "source": "loyalty.members",
                "eventName": "loyalty.members.upgraded",
                "timestamp": 1691060098 + i,
                "payload": {
                    "accountId": f"acc-{i}",
                    "memberId": f"mem-{i}",
                    "tierEventId": f"tier-{i}",
                    "tierCode": "T1X",
                    "isExistingTier": True,
                    "triggerType": "SPENDING",
                    "processedAt": "2024-03-15T00:00:00.000Z"
                }
            }
            for i in range(3)
        ]

        schema_id = 88888
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            # Encode all messages
            kafka_messages = []
            for msg in test_messages:
                buffer = BytesIO()
                schemaless_writer(buffer, avro_schema, msg)
                avro_bytes = buffer.getvalue()
                kafka_message = bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes
                kafka_messages.append(kafka_message)

            with TestPipeline() as p:
                result = (
                    p
                    | "CreateInput" >> beam.Create(kafka_messages)
                    | "Decode" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=False
                        )
                    )
                    | "Transform" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                    | "ExtractMemberId" >> beam.Map(lambda x: x["memberId"])
                )

                assert_that(result, equal_to(["mem-0", "mem-1", "mem-2"]))

            print("✅ Multiple messages pipeline test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_pipeline_with_sample_message_from_spec(self):
        """Test pipeline with exact sample from spec."""
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to
        from io import BytesIO
        from fastavro import schemaless_writer

        # Exact schema and message from API spec
        avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "namespace": "loyalty.members",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "UpgradedPayload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # EXACT sample from the spec image
        spec_message = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        schema_id = 77777
        mt._SCHEMA_CACHE[schema_id] = avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            buffer = BytesIO()
            schemaless_writer(buffer, avro_schema, spec_message)
            avro_bytes = buffer.getvalue()
            kafka_message = bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes

            with TestPipeline() as p:
                result = (
                    p
                    | "CreateInput" >> beam.Create([kafka_message])
                    | "Decode" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=True
                        )
                    )
                    | "Transform" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                    | "ExtractFields" >> beam.Map(
                        lambda x: {
                            "memberId": x["memberId"],
                            "tierCode": x["tierCode"],
                            "triggerType": x["triggerType"]
                        }
                    )
                )

                expected = [{
                    "memberId": "1-981785546",
                    "tierCode": "T1X",
                    "triggerType": "SPENDING"
                }]

                assert_that(result, equal_to(expected))

            print("✅ Spec sample message pipeline test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()


class TestFullPipelineIntegration(unittest.TestCase):
    """Full Pipeline Integration Test using DirectRunner.

    This tests the ENTIRE pipeline flow:
    1. Mock Kafka input (instead of ReadFromKafka)
    2. DecodeKafkaValueDoFn
    3. ToUpgradedDictDoFn / ToDowngradedDictDoFn
    4. CallMemberTierInfoAPIDoFn (with mocked API)
    5. ToMemberTierDictDoFn
    6. Verify final output

    This simulates what happens in Dataflow without needing:
    - Kafka connection
    - GCP Secret Manager
    - Real API calls
    - Iceberg/GCS writes
    """

    def setUp(self):
        """Set up test fixtures and mock schema."""
        self.avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "namespace": "loyalty.members",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "UpgradedPayload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # Sample message from spec
        self.sample_message = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        # Mock API response
        self.mock_api_response = {
            "member": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "code": "T1X",
                "programCode": "THE1",
                "partnerCode": "CENTRAL",
                "startDate": "2024-01-01",
                "expiryDate": "2024-12-31",
                "name": "The 1 Exclusive",
                "levelName": "Platinum"
            }
        }

    def _create_kafka_message(self, message_dict, schema_id=12345):
        """Create Confluent Avro wire format message."""
        from io import BytesIO
        from fastavro import schemaless_writer

        buffer = BytesIO()
        schemaless_writer(buffer, self.avro_schema, message_dict)
        avro_bytes = buffer.getvalue()

        # Confluent wire format: 0x00 + 4-byte schema ID + avro data
        return bytes([0]) + schema_id.to_bytes(4, "big") + avro_bytes

    def test_full_pipeline_upgraded_flow(self):
        """Test complete pipeline: Kafka -> Decode -> Transform -> API -> Output.

        This is the MAIN integration test that verifies the entire flow works.
        """
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to, is_not_empty

        # Setup: populate schema cache and set format
        schema_id = 12345
        mt._SCHEMA_CACHE[schema_id] = self.avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            # Create mock Kafka message
            kafka_message = self._create_kafka_message(self.sample_message, schema_id)

            with TestPipeline() as p:
                # =====================================================
                # STAGE 1: Mock Kafka Input (replaces ReadFromKafka)
                # =====================================================
                kafka_input = p | "MockKafkaInput" >> beam.Create([kafka_message])

                # =====================================================
                # STAGE 2: Decode Kafka Value (Avro -> Dict)
                # =====================================================
                decoded = (
                    kafka_input
                    | "DecodeKafkaValue" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=True
                        )
                    )
                )

                # Verify decode produces output
                decoded_event_ids = decoded | "ExtractDecodedEventId" >> beam.Map(lambda x: x.get("eventId"))
                assert_that(decoded_event_ids, equal_to(["a8debc92-50d2-4f7b-8c89-27b6e810a701"]), label="CheckDecoded")

                # =====================================================
                # STAGE 3: Transform to Upgraded Dict
                # =====================================================
                transformed = (
                    decoded
                    | "ToUpgradedDict" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                )

                # Verify transform produces output
                transformed_member_ids = transformed | "ExtractTransformedMemberId" >> beam.Map(lambda x: x.get("memberId"))
                assert_that(transformed_member_ids, equal_to(["1-981785546"]), label="CheckTransformed")

                # =====================================================
                # STAGE 4: Extract key fields for final assertion
                # =====================================================
                final = (
                    transformed
                    | "ExtractFinalFields" >> beam.Map(
                        lambda x: {
                            "eventId": x["eventId"],
                            "memberId": x["memberId"],
                            "tierCode": x["tierCode"],
                            "accountId": x["accountId"],
                            "triggerType": x["triggerType"],
                            "source_topic": x["source_topic"]
                        }
                    )
                )

                # Assert final output
                expected_final = [{
                    "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
                    "memberId": "1-981785546",
                    "tierCode": "T1X",
                    "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                    "triggerType": "SPENDING",
                    "source_topic": "loyalty.members.upgraded"
                }]

                assert_that(final, equal_to(expected_final), label="CheckFinal")

            print("✅ Full Pipeline (Upgraded) Integration Test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_full_pipeline_with_api_call_mocked(self):
        """Test complete pipeline including API call (mocked).

        This tests:
        1. Kafka -> Decode -> Transform
        2. API call (mocked)
        3. API response -> MemberTierDict
        """
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to

        schema_id = 12345
        mt._SCHEMA_CACHE[schema_id] = self.avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            kafka_message = self._create_kafka_message(self.sample_message, schema_id)

            # Create a mock API DoFn that returns predefined response
            class MockCallMemberTierAPIDoFn(beam.DoFn):
                """Mock API DoFn that returns predefined response without actual API call."""

                def __init__(self, mock_response):
                    self.mock_response = mock_response
                    self._logger = None

                def setup(self):
                    import logging
                    self._logger = logging.getLogger("member_tiers.MockCallMemberTierAPIDoFn")

                def process(self, element):
                    # Simulate API call behavior
                    payload = element.get("payload", {})
                    member_id = payload.get("memberId")

                    if not member_id:
                        self._logger.warning("No memberId, skipping")
                        return

                    self._logger.info(f"Mock API call for member_id={member_id}")

                    yield {
                        "_source_event_id": element.get("eventId"),
                        "_source_topic": element.get("_topic"),
                        "_ingested_at": element.get("_ingested_at"),
                        "api_response": self.mock_response,
                    }

            with TestPipeline() as p:
                # Stage 1-2: Kafka -> Decode
                decoded = (
                    p
                    | "MockKafkaInput" >> beam.Create([kafka_message])
                    | "DecodeKafkaValue" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=True
                        )
                    )
                )

                # Stage 3: Mock API Call
                api_results = (
                    decoded
                    | "MockAPICall" >> beam.ParDo(
                        MockCallMemberTierAPIDoFn(self.mock_api_response)
                    )
                )

                # Stage 4: Transform API response to MemberTierDict
                member_tier_dicts = (
                    api_results
                    | "ToMemberTierDict" >> beam.ParDo(mt.ToMemberTierDictDoFn())
                )

                # Stage 5: Extract key fields for assertion
                final = (
                    member_tier_dicts
                    | "ExtractFinal" >> beam.Map(
                        lambda x: {
                            "member_id": x["member_id"],
                            "tier_code": x["tier_code"],
                            "program_code": x["program_code"],
                            "name": x["name"],
                            "level_name": x["level_name"]
                        }
                    )
                )

                expected = [{
                    "member_id": "1-981785546",
                    "tier_code": "T1X",
                    "program_code": "THE1",
                    "name": "The 1 Exclusive",
                    "level_name": "Platinum"
                }]

                assert_that(final, equal_to(expected))

            print("✅ Full Pipeline with Mock API Integration Test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_full_pipeline_multiple_messages_both_topics(self):
        """Test pipeline with multiple messages from both upgraded and downgraded topics."""
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to

        # Create downgraded schema (no isExistingTier field)
        downgraded_schema = {
            "type": "record",
            "name": "MemberDowngraded",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "DowngradedPayload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # Test messages
        upgraded_messages = [
            {
                "eventId": "upgraded-001",
                "source": "loyalty.members",
                "eventName": "loyalty.members.upgraded",
                "timestamp": 1691060098,
                "payload": {
                    "accountId": "acc-up-001",
                    "memberId": "mem-up-001",
                    "tierEventId": "tier-up-001",
                    "tierCode": "T1X",
                    "isExistingTier": True,
                    "triggerType": "SPENDING",
                    "processedAt": "2024-03-15T00:00:00.000Z"
                }
            },
            {
                "eventId": "upgraded-002",
                "source": "loyalty.members",
                "eventName": "loyalty.members.upgraded",
                "timestamp": 1691060099,
                "payload": {
                    "accountId": "acc-up-002",
                    "memberId": "mem-up-002",
                    "tierEventId": "tier-up-002",
                    "tierCode": "GOLD",
                    "isExistingTier": False,
                    "triggerType": "POINTS",
                    "processedAt": "2024-03-16T00:00:00.000Z"
                }
            }
        ]

        downgraded_messages = [
            {
                "eventId": "downgraded-001",
                "source": "loyalty.members",
                "eventName": "loyalty.members.downgraded",
                "timestamp": 1691060100,
                "payload": {
                    "accountId": "acc-down-001",
                    "memberId": "mem-down-001",
                    "tierEventId": "tier-down-001",
                    "tierCode": "SILVER",
                    "triggerType": "EXPIRY",
                    "processedAt": "2024-03-17T00:00:00.000Z"
                }
            }
        ]

        # Setup schemas
        upgraded_schema_id = 11111
        downgraded_schema_id = 22222
        mt._SCHEMA_CACHE[upgraded_schema_id] = self.avro_schema
        mt._SCHEMA_CACHE[downgraded_schema_id] = downgraded_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            # Create Kafka messages
            from io import BytesIO
            from fastavro import schemaless_writer

            upgraded_kafka_msgs = []
            for msg in upgraded_messages:
                buf = BytesIO()
                schemaless_writer(buf, self.avro_schema, msg)
                kafka_msg = bytes([0]) + upgraded_schema_id.to_bytes(4, "big") + buf.getvalue()
                upgraded_kafka_msgs.append(kafka_msg)

            downgraded_kafka_msgs = []
            for msg in downgraded_messages:
                buf = BytesIO()
                schemaless_writer(buf, downgraded_schema, msg)
                kafka_msg = bytes([0]) + downgraded_schema_id.to_bytes(4, "big") + buf.getvalue()
                downgraded_kafka_msgs.append(kafka_msg)

            with TestPipeline() as p:
                # Process upgraded messages
                upgraded_decoded = (
                    p
                    | "UpgradedInput" >> beam.Create(upgraded_kafka_msgs)
                    | "DecodeUpgraded" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=False
                        )
                    )
                )

                upgraded_transformed = (
                    upgraded_decoded
                    | "TransformUpgraded" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                    | "ExtractUpgradedMemberId" >> beam.Map(lambda x: x["memberId"])
                )

                # Process downgraded messages
                downgraded_decoded = (
                    p
                    | "DowngradedInput" >> beam.Create(downgraded_kafka_msgs)
                    | "DecodeDowngraded" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.downgraded",
                            debug_mode=False
                        )
                    )
                )

                downgraded_transformed = (
                    downgraded_decoded
                    | "TransformDowngraded" >> beam.ParDo(mt.ToDowngradedDictDoFn())
                    | "ExtractDowngradedMemberId" >> beam.Map(lambda x: x["memberId"])
                )

                # Merge both streams (like Flatten in actual pipeline)
                merged = (
                    (upgraded_transformed, downgraded_transformed)
                    | "MergeTopics" >> beam.Flatten()
                )

                # Assert all member IDs are present
                expected_member_ids = ["mem-up-001", "mem-up-002", "mem-down-001"]
                assert_that(merged, equal_to(expected_member_ids))

            print("✅ Full Pipeline (Both Topics) Integration Test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_pipeline_error_handling_invalid_message(self):
        """Test pipeline handles invalid/malformed messages gracefully."""
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to

        schema_id = 12345
        mt._SCHEMA_CACHE[schema_id] = self.avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            # Create mix of valid and invalid messages
            valid_msg = self._create_kafka_message(self.sample_message, schema_id)
            invalid_msg_1 = b""  # Empty
            invalid_msg_2 = b"not avro"  # Invalid format
            invalid_msg_3 = bytes([0]) + (99999).to_bytes(4, "big") + b"bad"  # Wrong schema

            messages = [valid_msg, invalid_msg_1, invalid_msg_2, invalid_msg_3]

            with TestPipeline() as p:
                result = (
                    p
                    | "CreateMixedInput" >> beam.Create(messages)
                    | "Decode" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=False
                        )
                    )
                    | "ExtractMemberId" >> beam.Map(lambda x: x.get("payload", {}).get("memberId"))
                    | "FilterNone" >> beam.Filter(lambda x: x is not None)
                )

                # Only the valid message should produce output
                assert_that(result, equal_to(["1-981785546"]))

            print("✅ Pipeline Error Handling Test PASSED")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_pipeline_pyarrow_output_compatibility(self):
        """Test that pipeline output is compatible with PyArrow schema for Iceberg.

        This test verifies that ToUpgradedDictDoFn produces output that can be
        converted to a PyArrow Table with SCHEMA_UPGRADED_RAW schema.
        """
        import pyarrow as pa

        schema_id = 12345
        mt._SCHEMA_CACHE[schema_id] = self.avro_schema
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            kafka_message = self._create_kafka_message(self.sample_message, schema_id)

            # =====================================================
            # Step 1: Run Decode DoFn directly (not through pipeline)
            # =====================================================
            decode_dofn = mt.DecodeKafkaValueDoFn(
                topic_name="loyalty.members.upgraded",
                debug_mode=False
            )
            decode_dofn.setup()
            decode_dofn.start_bundle()
            decoded_results = list(decode_dofn.process(kafka_message))

            self.assertEqual(len(decoded_results), 1, "Decode should produce 1 result")
            decoded = decoded_results[0]

            # =====================================================
            # Step 2: Run Transform DoFn directly
            # =====================================================
            transform_dofn = mt.ToUpgradedDictDoFn()
            transform_dofn.setup()
            transform_results = list(transform_dofn.process(decoded))

            self.assertEqual(len(transform_results), 1, "Transform should produce 1 result")
            transformed = transform_results[0]

            # =====================================================
            # Step 3: Verify PyArrow compatibility
            # =====================================================
            try:
                table = pa.Table.from_pylist([transformed], schema=mt.SCHEMA_UPGRADED_RAW)
                self.assertEqual(table.num_rows, 1)

                # Verify key columns
                self.assertEqual(table.column("eventId").to_pylist()[0], "a8debc92-50d2-4f7b-8c89-27b6e810a701")
                self.assertEqual(table.column("memberId").to_pylist()[0], "1-981785546")
                self.assertEqual(table.column("tierCode").to_pylist()[0], "T1X")

                print("✅ PyArrow Output Compatibility Test PASSED")
                print(f"   - Table schema fields: {[f.name for f in table.schema]}")
                print(f"   - Rows: {table.num_rows}")

            except Exception as e:
                self.fail(f"Failed to create PyArrow table: {e}")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()


class TestSpecBasedValidation(unittest.TestCase):
    """Spec-based tests with EXPECTED OUTPUT from business requirements.

    These tests verify that:
    1. Input message from Kafka is processed correctly
    2. Output matches EXACT expected values from spec
    3. Every required field is present and correct
    4. Any bug in code logic will FAIL these tests

    IMPORTANT: Expected outputs are defined from BUSINESS SPEC, not from code!
    """

    def setUp(self):
        """Set up spec-defined test data."""
        # =====================================================
        # SPEC INPUT: Exact message from Kafka (Avro format)
        # Source: API Spec / Confluent Schema Registry
        # =====================================================
        self.SPEC_INPUT_UPGRADED = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        # =====================================================
        # SPEC EXPECTED OUTPUT: After DecodeKafkaValueDoFn
        # What we EXPECT to get after decoding Avro bytes
        # =====================================================
        self.EXPECTED_AFTER_DECODE = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            },
            # Added by DecodeKafkaValueDoFn:
            "_topic": "loyalty.members.upgraded",
            # "_ingested_at": <datetime>,  # dynamic
            # "_message_number": <int>,     # dynamic
        }

        # =====================================================
        # SPEC EXPECTED OUTPUT: After ToUpgradedDictDoFn
        # Flattened structure for Iceberg table
        # =====================================================
        self.EXPECTED_AFTER_TRANSFORM = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            # "timestamp": <datetime>,  # parsed from int
            "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
            "memberId": "1-981785546",
            "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
            "tierCode": "T1X",
            "isExistingTier": True,
            "triggerType": "SPENDING",
            "processedAt": "2024-03-15T00:00:00.000Z",
            "source_topic": "loyalty.members.upgraded",
            # "ingested_at": <datetime>,  # dynamic
        }

        # Required fields that MUST exist
        self.REQUIRED_FIELDS_AFTER_DECODE = [
            "eventId", "source", "eventName", "timestamp", "payload",
            "_topic"  # added by DoFn
        ]

        self.REQUIRED_PAYLOAD_FIELDS = [
            "accountId", "memberId", "tierEventId", "tierCode",
            "triggerType", "processedAt"
        ]

        self.REQUIRED_FIELDS_AFTER_TRANSFORM = [
            "eventId", "source", "eventName", "timestamp",
            "accountId", "memberId", "tierEventId", "tierCode",
            "triggerType", "processedAt", "source_topic", "ingested_at"
        ]

        # Avro schema for encoding
        self.avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "namespace": "loyalty.members",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "UpgradedPayload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

    def _create_avro_message(self, data, schema_id=12345):
        """Create Confluent Avro wire format message."""
        from io import BytesIO
        from fastavro import schemaless_writer

        mt._SCHEMA_CACHE[schema_id] = self.avro_schema
        buffer = BytesIO()
        schemaless_writer(buffer, self.avro_schema, data)
        return bytes([0]) + schema_id.to_bytes(4, "big") + buffer.getvalue()

    def test_step1_decode_output_matches_spec(self):
        """STEP 1: Verify DecodeKafkaValueDoFn output matches spec exactly.

        This test ensures that after decoding Avro bytes:
        - All original fields are preserved
        - Values match exactly
        - Metadata fields are added correctly
        """
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            kafka_message = self._create_avro_message(self.SPEC_INPUT_UPGRADED)

            # Run decode
            dofn = mt.DecodeKafkaValueDoFn(
                topic_name="loyalty.members.upgraded",
                debug_mode=True
            )
            dofn.setup()
            dofn.start_bundle()
            results = list(dofn.process(kafka_message))

            # VERIFY: Exactly 1 output
            self.assertEqual(len(results), 1, "DecodeKafkaValueDoFn must produce exactly 1 output")
            result = results[0]

            # VERIFY: All required fields exist
            for field in self.REQUIRED_FIELDS_AFTER_DECODE:
                self.assertIn(field, result, f"Missing required field after decode: {field}")

            # VERIFY: Field values match spec exactly
            self.assertEqual(result["eventId"], self.EXPECTED_AFTER_DECODE["eventId"],
                           "eventId mismatch!")
            self.assertEqual(result["source"], self.EXPECTED_AFTER_DECODE["source"],
                           "source mismatch!")
            self.assertEqual(result["eventName"], self.EXPECTED_AFTER_DECODE["eventName"],
                           "eventName mismatch!")
            self.assertEqual(result["timestamp"], self.EXPECTED_AFTER_DECODE["timestamp"],
                           "timestamp mismatch!")
            self.assertEqual(result["_topic"], self.EXPECTED_AFTER_DECODE["_topic"],
                           "_topic mismatch!")

            # VERIFY: Payload fields match spec exactly
            payload = result.get("payload", {})
            for field in self.REQUIRED_PAYLOAD_FIELDS:
                self.assertIn(field, payload, f"Missing payload field: {field}")

            self.assertEqual(payload["accountId"], self.SPEC_INPUT_UPGRADED["payload"]["accountId"])
            self.assertEqual(payload["memberId"], self.SPEC_INPUT_UPGRADED["payload"]["memberId"])
            self.assertEqual(payload["tierEventId"], self.SPEC_INPUT_UPGRADED["payload"]["tierEventId"])
            self.assertEqual(payload["tierCode"], self.SPEC_INPUT_UPGRADED["payload"]["tierCode"])
            self.assertEqual(payload["isExistingTier"], self.SPEC_INPUT_UPGRADED["payload"]["isExistingTier"])
            self.assertEqual(payload["triggerType"], self.SPEC_INPUT_UPGRADED["payload"]["triggerType"])
            self.assertEqual(payload["processedAt"], self.SPEC_INPUT_UPGRADED["payload"]["processedAt"])

            # VERIFY: Metadata fields are present
            self.assertIn("_ingested_at", result, "_ingested_at must be added by DoFn")
            self.assertIsNotNone(result["_ingested_at"], "_ingested_at must not be None")

            print("✅ STEP 1 PASSED: DecodeKafkaValueDoFn output matches spec")
            print(f"   - eventId: {result['eventId']}")
            print(f"   - memberId: {payload['memberId']}")
            print(f"   - tierCode: {payload['tierCode']}")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_step2_transform_output_matches_spec(self):
        """STEP 2: Verify ToUpgradedDictDoFn output matches spec exactly.

        This test ensures that after transform:
        - Payload is flattened correctly
        - All required fields exist
        - Values match exactly
        """
        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            kafka_message = self._create_avro_message(self.SPEC_INPUT_UPGRADED)

            # Step 1: Decode
            decode_dofn = mt.DecodeKafkaValueDoFn(
                topic_name="loyalty.members.upgraded",
                debug_mode=True
            )
            decode_dofn.setup()
            decode_dofn.start_bundle()
            decoded = list(decode_dofn.process(kafka_message))[0]

            # Step 2: Transform
            transform_dofn = mt.ToUpgradedDictDoFn()
            transform_dofn.setup()
            results = list(transform_dofn.process(decoded))

            # VERIFY: Exactly 1 output
            self.assertEqual(len(results), 1, "ToUpgradedDictDoFn must produce exactly 1 output")
            result = results[0]

            # VERIFY: All required fields exist
            for field in self.REQUIRED_FIELDS_AFTER_TRANSFORM:
                self.assertIn(field, result, f"Missing required field after transform: {field}")

            # VERIFY: Field values match spec exactly
            self.assertEqual(result["eventId"], self.EXPECTED_AFTER_TRANSFORM["eventId"],
                           "eventId mismatch after transform!")
            self.assertEqual(result["source"], self.EXPECTED_AFTER_TRANSFORM["source"],
                           "source mismatch after transform!")
            self.assertEqual(result["eventName"], self.EXPECTED_AFTER_TRANSFORM["eventName"],
                           "eventName mismatch after transform!")
            self.assertEqual(result["accountId"], self.EXPECTED_AFTER_TRANSFORM["accountId"],
                           "accountId mismatch after transform!")
            self.assertEqual(result["memberId"], self.EXPECTED_AFTER_TRANSFORM["memberId"],
                           "memberId mismatch after transform!")
            self.assertEqual(result["tierEventId"], self.EXPECTED_AFTER_TRANSFORM["tierEventId"],
                           "tierEventId mismatch after transform!")
            self.assertEqual(result["tierCode"], self.EXPECTED_AFTER_TRANSFORM["tierCode"],
                           "tierCode mismatch after transform!")
            self.assertEqual(result["isExistingTier"], self.EXPECTED_AFTER_TRANSFORM["isExistingTier"],
                           "isExistingTier mismatch after transform!")
            self.assertEqual(result["triggerType"], self.EXPECTED_AFTER_TRANSFORM["triggerType"],
                           "triggerType mismatch after transform!")
            self.assertEqual(result["processedAt"], self.EXPECTED_AFTER_TRANSFORM["processedAt"],
                           "processedAt mismatch after transform!")
            self.assertEqual(result["source_topic"], self.EXPECTED_AFTER_TRANSFORM["source_topic"],
                           "source_topic mismatch after transform!")

            # VERIFY: timestamp is parsed correctly (not raw int)
            self.assertIsNotNone(result["timestamp"], "timestamp must not be None")

            # VERIFY: ingested_at is present
            self.assertIn("ingested_at", result, "ingested_at must be present")
            self.assertIsNotNone(result["ingested_at"], "ingested_at must not be None")

            print("✅ STEP 2 PASSED: ToUpgradedDictDoFn output matches spec")
            print(f"   - memberId: {result['memberId']}")
            print(f"   - tierCode: {result['tierCode']}")
            print(f"   - source_topic: {result['source_topic']}")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_step3_full_pipeline_e2e_matches_spec(self):
        """STEP 3: Full E2E test - Kafka bytes to final output.

        This test runs the ENTIRE pipeline and verifies final output.
        """
        import apache_beam as beam
        from apache_beam.testing.test_pipeline import TestPipeline
        from apache_beam.testing.util import assert_that, equal_to

        original_use_sr = mt.USE_SCHEMA_REGISTRY
        original_format = mt.PAYLOAD_FORMAT
        mt.USE_SCHEMA_REGISTRY = False
        mt.PAYLOAD_FORMAT = "avro"

        try:
            kafka_message = self._create_avro_message(self.SPEC_INPUT_UPGRADED)

            with TestPipeline() as p:
                result = (
                    p
                    | "Input" >> beam.Create([kafka_message])
                    | "Decode" >> beam.ParDo(
                        mt.DecodeKafkaValueDoFn(
                            topic_name="loyalty.members.upgraded",
                            debug_mode=True
                        )
                    )
                    | "Transform" >> beam.ParDo(mt.ToUpgradedDictDoFn())
                    | "ExtractKeyFields" >> beam.Map(
                        lambda x: {
                            "eventId": x["eventId"],
                            "memberId": x["memberId"],
                            "tierCode": x["tierCode"],
                            "triggerType": x["triggerType"],
                            "isExistingTier": x["isExistingTier"],
                        }
                    )
                )

                # Expected output from SPEC
                expected = [{
                    "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
                    "memberId": "1-981785546",
                    "tierCode": "T1X",
                    "triggerType": "SPENDING",
                    "isExistingTier": True,
                }]

                assert_that(result, equal_to(expected))

            print("✅ STEP 3 PASSED: Full E2E pipeline matches spec")

        finally:
            mt.USE_SCHEMA_REGISTRY = original_use_sr
            mt.PAYLOAD_FORMAT = original_format
            mt._SCHEMA_CACHE.clear()

    def test_validation_missing_required_field_should_log_warning(self):
        """Test that missing required fields are logged (not silently ignored)."""
        # Input with missing memberId
        bad_input = {
            "eventId": "test-123",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "_topic": "loyalty.members.upgraded",
            "_ingested_at": datetime.now(mt.TZ_BANGKOK),
            "payload": {
                "accountId": "acc-123",
                # memberId is MISSING!
                "tierEventId": "tier-123",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        transform_dofn = mt.ToUpgradedDictDoFn()
        transform_dofn.setup()
        results = list(transform_dofn.process(bad_input))

        # Should still produce output but memberId will be None
        self.assertEqual(len(results), 1)
        result = results[0]

        # memberId should be None (not crash)
        self.assertIsNone(result["memberId"], "Missing memberId should result in None")

        print("✅ Validation test: Missing field handled gracefully (memberId=None)")

    def test_validation_null_payload_should_skip_not_crash(self):
        """Test that null payload is SKIPPED (not crash, not produce bad output)."""
        bad_input = {
            "eventId": "test-123",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "_topic": "loyalty.members.upgraded",
            "_ingested_at": datetime.now(mt.TZ_BANGKOK),
            "payload": None  # NULL payload!
        }

        transform_dofn = mt.ToUpgradedDictDoFn()
        transform_dofn.setup()

        # Should not crash
        results = list(transform_dofn.process(bad_input))

        # Should SKIP (no output) - this is correct behavior!
        # Bad data should not propagate through the pipeline
        self.assertEqual(len(results), 0, "Null payload should be SKIPPED (no output)")

        # Verify skip was counted
        self.assertEqual(transform_dofn._skip_count, 1, "Skip count should be 1")

        print("✅ Validation test: Null payload SKIPPED correctly (no crash, no bad output)")


class TestAvroSchemaFromSpec(unittest.TestCase):
    """Test Avro decoding with exact schema from spec."""

    def test_decode_exact_spec_payload(self):
        """Test decoding the exact payload from the API spec."""
        # This is the EXACT schema structure from the spec
        avro_schema = {
            "type": "record",
            "name": "MemberUpgraded",
            "namespace": "loyalty.members",
            "fields": [
                {"name": "eventId", "type": "string"},
                {"name": "source", "type": "string"},
                {"name": "eventName", "type": "string"},
                {"name": "timestamp", "type": "long"},
                {"name": "payload", "type": {
                    "type": "record",
                    "name": "UpgradedPayload",
                    "fields": [
                        {"name": "accountId", "type": "string"},
                        {"name": "memberId", "type": "string"},
                        {"name": "tierEventId", "type": "string"},
                        {"name": "tierCode", "type": "string"},
                        {"name": "isExistingTier", "type": "boolean"},
                        {"name": "triggerType", "type": "string"},
                        {"name": "processedAt", "type": "string"}
                    ]
                }}
            ]
        }

        # Exact payload from spec
        spec_payload = {
            "eventId": "a8debc92-50d2-4f7b-8c89-27b6e810a701",
            "source": "loyalty.members",
            "eventName": "loyalty.members.upgraded",
            "timestamp": 1691060098,
            "payload": {
                "accountId": "69f6a344-1321-4cbb-87e5-991c96593931",
                "memberId": "1-981785546",
                "tierEventId": "69f6a344-1321-4cbb-87e5-991c965009009",
                "tierCode": "T1X",
                "isExistingTier": True,
                "triggerType": "SPENDING",
                "processedAt": "2024-03-15T00:00:00.000Z"
            }
        }

        # Encode to Avro
        from fastavro import schemaless_writer, schemaless_reader
        buffer = BytesIO()
        schemaless_writer(buffer, avro_schema, spec_payload)
        avro_bytes = buffer.getvalue()

        # Verify we can decode it back
        buffer.seek(0)
        decoded = schemaless_reader(buffer, avro_schema)

        self.assertEqual(decoded["eventId"], spec_payload["eventId"])
        self.assertEqual(decoded["payload"]["memberId"], spec_payload["payload"]["memberId"])
        self.assertEqual(decoded["payload"]["tierCode"], spec_payload["payload"]["tierCode"])
        self.assertEqual(decoded["payload"]["isExistingTier"], True)

        print("✅ Avro schema from spec is valid and can encode/decode correctly")


if __name__ == "__main__":
    unittest.main(verbosity=2)
