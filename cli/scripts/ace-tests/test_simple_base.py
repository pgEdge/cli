import pytest
import psycopg
import json
import re


@pytest.mark.usefixtures("prepare_databases")
@pytest.mark.abstract_base
class TestSimpleBase:
    """Abstract base class for ACE operation tests.
    This class should not be run directly, but instead should be inherited
    by concrete test classes."""

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def _introduce_differences(
        self, config, node, table_name, column_name, key_column,
    ):
        """Helper method to introduce differences in a table

        Args:
            node: The node to introduce differences on
            table_name: The table name (with schema)
            column_name: The column to modify (default: "first_name")

        Returns:
            Set of modified row indices
        """
        schema, table = table_name.split(".")
        params = {
            "host": node if node != "n1" else "localhost",
            "dbname": "demo",
            "user": "admin",
        }
        if config.USE_CERT_AUTH:
            params["sslmode"] = "verify-full"
            params["sslrootcert"] = config.CA_CERT_FILE
            params["sslcert"] = config.ACE_USER_CERT_FILE
            params["sslkey"] = config.ACE_USER_KEY_FILE

        conn = psycopg.connect(**params)
        cur = conn.cursor()

        # Note: column_name should be quoted if it contains uppercase
        cur.execute(
            f"""
            WITH random_rows AS (
                SELECT \"{key_column}\"
                FROM {schema}.\"{table}\"
                ORDER BY random()
                LIMIT 50
            )
            UPDATE {schema}.\"{table}\"
            SET \"{column_name}\" = \"{column_name}\" || '-modified'
            WHERE \"{key_column}\" IN (SELECT \"{key_column}\" FROM random_rows)
            RETURNING \"{key_column}\", \"{column_name}\";
        """
        )

        modified_rows = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

        return {row[0] for row in modified_rows}  # Return set of modified indices

    def test_database_connectivity(self, config, nodes):
        """Test that we can connect to all prepared databases"""
        for node in nodes:
            try:
                params = {
                    "host": node if node != "n1" else "localhost",
                    "dbname": "demo",
                    "user": "admin",
                }
                if config.USE_CERT_AUTH:
                    params["sslmode"] = "verify-full"
                    params["sslrootcert"] = config.CA_CERT_FILE
                    params["sslcert"] = config.ACE_USER_CERT_FILE
                    params["sslkey"] = config.ACE_USER_KEY_FILE

                conn = psycopg.connect(**params)
                assert conn is not None
                conn.close()
            except Exception as e:
                pytest.fail(f"Failed to connect to node {node}: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        """Test table diff on cluster eqn-t9da for specified table"""

        cli.table_diff_cli("eqn-t9da", table_name)
        captured = capsys.readouterr()
        output = captured.out
        assert (
            "tables match ok" in output.lower()
        ), f"Table diff failed. Output: {output}"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_differences(
        self,
        cli,
        capsys,
        config,
        table_name,
        column_name,
        key_column,
        diff_file_path,
    ):
        """Test table diff when differences exist between nodes"""
        try:
            # Introduce differences using the helper method
            modified_indices = self._introduce_differences(
                config, "n2", table_name, column_name, key_column
            )

            # Execute table diff and verify results
            cli.table_diff_cli("eqn-t9da", table_name)

            # Capture the output
            captured = capsys.readouterr()
            output = captured.out

            # Remove garbage characters from the output
            clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)

            # Search in the cleaned output
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Read and parse the diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify the number of differences matches our modifications
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
            ), "Expected 50 differences,"
            f" but found {len(diff_data['diffs']['n1/n2']['n2'])}"

            # Verify each modified row is present in the diff
            diff_indices = {
                diff[key_column] for diff in diff_data["diffs"]["n1/n2"]["n2"]
            }  # Set of indices from diff file

            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                assert diff[column_name].endswith(
                    "-modified"
                ), f"Modified row {diff[key_column]} doesn't have expected suffix"

            # Verify the control rows are not modified
            for diff in diff_data["diffs"]["n1/n2"]["n1"]:
                assert not diff[column_name].endswith(
                    "-modified"
                ), f"Control row {diff[key_column]} shouldn't have modification suffix"

        except Exception as e:
            pytest.fail(f"Failed to introduce diffs: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        """Test table repair on cluster eqn-t9da for specified table"""
        cli.table_repair_cli(
            "eqn-t9da",
            table_name,
            diff_file_path.path,
            source_of_truth="n1",
        )

        captured = capsys.readouterr()
        output = captured.out
        assert (
            "successfully applied diffs" in output.lower()
        ), f"Table repair failed. Output: {output}"

        # Verify the table is repaired
        cli.table_diff_cli("eqn-t9da", table_name)

        captured = capsys.readouterr()
        output = captured.out
        assert (
            "tables match ok" in output.lower()
        ), f"Table diff after repair failed. Output: {output}"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(
        self, cli, capsys, config, table_name, key_column, diff_file_path
    ):
        """Test table rerun temptable on cluster eqn-t9da for specified table"""

        # We will start by introducing diffs to the customers table on n2

        schema, table = table_name.split(".")

        try:
            params = {
                "host": "n2",
                "dbname": "demo",
                "user": "admin",
            }
            if config.USE_CERT_AUTH:
                params["sslmode"] = "verify-full"
                params["sslrootcert"] = config.CA_CERT_FILE
                params["sslcert"] = config.ACE_USER_CERT_FILE
                params["sslkey"] = config.ACE_USER_KEY_FILE

            conn = psycopg.connect(**params)
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE {schema}.\"{table}\"
                SET city = 'Casablanca'
                WHERE \"{key_column}\" < 101
                """
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Failed to introduce diffs on n2: {str(e)}")

        # Running the table-diff to get the diff file
        cli.table_diff_cli("eqn-t9da", table_name)

        # Capture the output
        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)

        # Search for the diff file path in the output
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        path = match.group(1)

        cli.table_rerun_cli(
            "eqn-t9da",
            path,
            table_name,
            "demo",  # dbname
            False,  # quiet
            "hostdb",  # behaviour
        )

        rerun_captured = capsys.readouterr()
        rerun_output = rerun_captured.out

        clean_rerun_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", rerun_output
        )

        match = re.search(
            r"diffs written out to (.+\.json)", clean_rerun_output.lower()
        )

        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        # Read the diff file into a dictionary
        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # Verify the diff file is correct
        assert len(diff_data["diffs"]["n1/n2"]["n2"]) == 100, "Expected 100 differences"

        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            assert diff["city"] == "Casablanca", "Expected city to be 'Casablanca'"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name, diff_file_path):
        """Test table rerun multiprocessing on cluster eqn-t9da"""

        # We have already introduced diffs in the previous test.
        # We will now rerun the diffs using multiprocessing

        cli.table_rerun_cli(
            "eqn-t9da",
            diff_file_path.path,
            table_name,
            "demo",  # dbname
            False,  # quiet
            "multiprocessing",  # behaviour
        )

        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)

        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())

        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        # Read the diff file into a dictionary
        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # Verify we still have 100 diffs
        assert len(diff_data["diffs"]["n1/n2"]["n2"]) == 100, "Expected 100 differences"

        # Verify the diffs are correct
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            assert diff["city"] == "Casablanca", "Expected city to be 'Casablanca'"

        # Now that we have verified diffs through both methods, we can use repair
        # to restore the state of the table
        cli.table_repair_cli(
            "eqn-t9da",
            table_name,
            diff_file_path.path,
            source_of_truth="n1",
        )

        captured = capsys.readouterr()
        output = captured.out

        assert (
            "successfully applied diffs" in output.lower()
        ), f"Table repair failed. Output: {output}"
