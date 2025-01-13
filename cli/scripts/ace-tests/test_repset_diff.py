import json
import re
import pytest
import psycopg
from test_simple import TestSimple


@pytest.mark.usefixtures("prepare_databases")
class TestRepsetDiff(TestSimple):
    """Test class for repset-diff functionality"""

    def _introduce_differences(
        self, ace_conf, node, table_name, column_name, key_column
    ):
        """Helper method to introduce differences in a table"""
        try:
            params = {
                "host": node,
                "dbname": "demo",
                "user": "admin",
                "application_name": "ace-tests",
            }
            if ace_conf.USE_CERT_AUTH:
                params["sslmode"] = "verify-full"
                params["sslrootcert"] = ace_conf.CA_CERT_FILE
                params["sslcert"] = ace_conf.ADMIN_CERT_FILE
                params["sslkey"] = ace_conf.ADMIN_KEY_FILE

            conn = psycopg.connect(**params)
            cur = conn.cursor()

            # Modify 50 rows in the table
            cur.execute(
                f"""
                UPDATE {table_name}
                SET {column_name} = {column_name} || '-modified'
                WHERE {key_column} < 50
                RETURNING {key_column}
            """
            )

            modified_rows = cur.fetchall()
            modified_indices = {row[0] for row in modified_rows}

            conn.commit()
            cur.close()
            conn.close()

            return modified_indices

        except Exception as e:
            pytest.fail(f"Failed to introduce differences: {str(e)}")

    def test_basic_repset_diff(self, cli, capsys, ace_conf, diff_file_path):
        """Test basic repset-diff functionality"""
        try:
            # First introduce some differences in the customers table
            modified_indices = self._introduce_differences(
                ace_conf, "n2", "public.customers", "first_name", "index"
            )

            # Run repset-diff
            cli.repset_diff_cli("eqn-t9da", "demo_replication_set")

            # Capture and clean the output
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )

            # Verify differences were found
            assert (
                "differences found" in clean_output.lower()
            ), "No differences detected"

            # Get the diff file path
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Read and verify the diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify the number of differences matches our modifications
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
            ), "Expected 50 differences"

            # Verify each modified row is present in the diff
            diff_indices = {diff["index"] for diff in diff_data["diffs"]["n1/n2"]["n2"]}
            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    def test_repset_diff_skip_tables(self, cli, capsys, ace_conf):
        """Test repset-diff with skip-tables option"""
        try:
            # First introduce some differences in the customers table
            self._introduce_differences(
                ace_conf, "n2", "public.customers", "first_name", "index"
            )

            # Run repset-diff with customers table skipped
            cli.repset_diff_cli(
                "eqn-t9da", "demo_replication_set", skip_tables=["public.customers"]
            )

            # Capture and clean the output
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )

            # Verify the customers table was skipped
            assert (
                "skipping table public.customers" in clean_output.lower()
            ), "Table not skipped"
            assert (
                "tables match ok" in clean_output.lower()
            ), "Differences found in non-skipped tables"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    def test_repset_diff_skip_file(self, cli, capsys, ace_conf, tmp_path):
        """Test repset-diff with skip-file option"""
        try:
            # Create a skip file
            skip_file = tmp_path / "skip.txt"
            skip_file.write_text("public.customers\n")

            # First introduce some differences in the customers table
            self._introduce_differences(
                ace_conf, "n2", "public.customers", "first_name", "index"
            )

            # Run repset-diff with skip file
            cli.repset_diff_cli(
                "eqn-t9da", "demo_replication_set", skip_file=str(skip_file)
            )

            # Capture and clean the output
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )

            # Verify the customers table was skipped
            assert (
                "skipping table public.customers" in clean_output.lower()
            ), "Table not skipped"
            assert (
                "tables match ok" in clean_output.lower()
            ), "Differences found in non-skipped tables"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
