import pytest
import psycopg
import json
import re
import time
from datetime import datetime


@pytest.mark.usefixtures("prepare_databases")
class TestReplication:
    """Group of tests for various PostgreSQL data types"""

    test_data = {
        "public.datatypes_test": {
            "key_column": "id",
            "row": {
                "id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14",
                "int_col": 999,
                "float_col": 9.99,
                "array_col": [9, 9, 9],
                "json_col": {"test": "value"},
                "bytea_col": b"test",
                "point_col": "(9.9,9.9)",
                "text_col": "test replication",
                "text_array_col": ["test", "array"],
            },
        },
        "public.customers": {
            "key_column": "index",
            "row": {
                "index": 10001,
                "customer_id": "TEST001",
                "first_name": "Test",
                "last_name": "User",
                "company": "Test Company",
                "city": "Test City",
                "country": "Test Country",
                "phone_1": "123-456-7890",
                "phone_2": "098-765-4321",
                "email": "test@example.com",
                "subscription_date": datetime.now(),
                "website": "www.test.com",
            },
        },
    }

    @pytest.mark.parametrize(
        "table_name", ["public.datatypes_test", "public.customers"]
    )
    def test_replication(
        self,
        cli,
        capsys,
        table_name,
    ):
        """Test that a row inserted on one node gets replicated to others"""
        try:
            # Get test data for the current table
            test_data = self.test_data[table_name]
            test_row = test_data["row"]

            # Insert a new row into n2
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()

            # Create the INSERT statement dynamically
            columns = list(test_row.keys())
            placeholders = ["%s"] * len(columns)
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """

            # Convert values for database insertion
            values = []
            for val in test_row.values():
                if isinstance(val, dict):
                    values.append(json.dumps(val))
                elif isinstance(val, datetime):
                    values.append(val.isoformat())
                else:
                    values.append(val)

            cur.execute(insert_sql, values)
            conn.commit()
            cur.close()
            conn.close()

            # Give some time for replication to occur
            time.sleep(2)

            # Execute table diff and verify results
            cli.table_diff_cli("eqn-t9da", table_name)

            # Capture and verify output
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )

            # Verify no differences are found (replication worked)
            assert (
                "tables match ok" in clean_output.lower()
            ), "Expected no differences after replication"

            # Clean up - delete the test row
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            key_column = test_data["key_column"]
            cur.execute(
                f"DELETE FROM {table_name} WHERE {key_column} = %s",
                (test_row[key_column],),
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
