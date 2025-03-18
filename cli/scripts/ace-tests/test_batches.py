import json
import pytest
import re
import psycopg


@pytest.mark.skip(reason="Skipping batches tests")
@pytest.mark.usefixtures("prepare_databases")
class TestBatches:

    def test_single_batch(self, cli, capsys):
        """Test that a single batch works"""
        cli.table_diff_cli("eqn-t9da", "public.customers")
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        assert "tables match ok" in clean_output.lower()

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_multiple_batches(
        self, cli, capsys, table_name, column_name, key_column, diff_file_path
    ):
        """Test prepared statements + optimisations when using multiple batches"""

        schema, table = table_name.split(".")

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute("SELECT spock.repair_mode(true)")
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
        conn.commit()
        cur.close()
        conn.close()

        cli.table_diff_cli(
            "eqn-t9da",
            table_name,
            block_rows=1000,
            batch_size=10,
            override_block_size=True,
        )
        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # Verify all differences are within filter range
        assert (
            len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
        ), "Expected 50 differences,"
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            assert diff[column_name].endswith(
                "-modified"
            ), "Modified row doesn't have expected value"
