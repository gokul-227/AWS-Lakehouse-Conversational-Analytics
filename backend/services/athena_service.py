"""Athena service — query execution and DDL operations."""

import os
import time
import boto3
from botocore.exceptions import ClientError


class AthenaService:
    """Manages Athena interactions for query execution and table management."""

    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.database = os.getenv("ATHENA_DATABASE", "lakechat_db")
        self.workgroup = os.getenv("ATHENA_WORKGROUP", "lakechat_workgroup")
        self.results_bucket = os.getenv("ATHENA_RESULTS_BUCKET", "lakechat-athena-results")
        self.data_bucket = os.getenv("S3_BUCKET_NAME", "lakechat-datasets")
        self.client = boto3.client("athena", region_name=self.region)

    def _run_query(self, sql: str, wait: bool = True) -> str:
        """Submit a query to Athena and optionally wait for completion."""
        response = self.client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": self.database},
            WorkGroup=self.workgroup,
        )
        query_id = response["QueryExecutionId"]

        if wait:
            self._wait_for_query(query_id)

        return query_id

    def _wait_for_query(self, query_id: str, timeout: int = 60):
        """Poll Athena until query completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.client.get_query_execution(QueryExecutionId=query_id)
            state = status["QueryExecution"]["Status"]["State"]
            if state == "SUCCEEDED":
                return
            if state in ("FAILED", "CANCELLED"):
                reason = status["QueryExecution"]["Status"].get("StateChangeReason", "Unknown error")
                raise Exception(f"Athena query {state}: {reason}")
            time.sleep(1)
        raise Exception("Athena query timed out.")

    def execute_query(self, sql: str) -> tuple[list, list]:
        """Execute a SELECT query and return (rows, columns)."""
        query_id = self._run_query(sql)

        results = self.client.get_query_results(QueryExecutionId=query_id)
        columns = [col["Label"] for col in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

        rows = []
        for row_data in results["ResultSet"]["Rows"][1:]:  # Skip header row
            row = {}
            for i, datum in enumerate(row_data["Data"]):
                row[columns[i]] = datum.get("VarCharValue", "")
            rows.append(row)

        return rows, columns

    def create_external_table(self, table_name: str, schema: list, s3_key: str, file_type: str):
        """Create an external table in Glue Data Catalog via Athena DDL."""
        columns_ddl = ", ".join(
            f"`{col['name']}` {self._map_type(col['type'])}" for col in schema
        )

        s3_location = f"s3://{self.data_bucket}/{'/'.join(s3_key.split('/')[:-1])}/"

        serde_map = {
            "csv": (
                "ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' "
                "WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '\"') "
                "STORED AS TEXTFILE"
            ),
            "json": (
                "ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe' "
                "STORED AS TEXTFILE"
            ),
            "parquet": "STORED AS PARQUET",
        }

        sql = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS `{self.database}`.`{table_name}` (
            {columns_ddl}
        )
        {serde_map.get(file_type, "STORED AS TEXTFILE")}
        LOCATION '{s3_location}'
        TBLPROPERTIES ('has_encrypted_data'='false')
        """

        self._run_query(sql)

    def drop_table(self, table_name: str):
        """Drop an external table."""
        if not table_name:
            return
        try:
            self._run_query(f"DROP TABLE IF EXISTS `{self.database}`.`{table_name}`")
        except Exception:
            pass

    @staticmethod
    def _map_type(python_type: str) -> str:
        """Map inferred Python types to Athena/Hive types."""
        mapping = {
            "int64": "BIGINT",
            "float64": "DOUBLE",
            "object": "STRING",
            "bool": "BOOLEAN",
            "datetime64": "TIMESTAMP",
            "string": "STRING",
            "integer": "BIGINT",
            "float": "DOUBLE",
            "boolean": "BOOLEAN",
        }
        return mapping.get(python_type, "STRING")
