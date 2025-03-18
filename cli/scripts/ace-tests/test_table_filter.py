import pytest
import psycopg
import json
import re


@pytest.mark.usefixtures("prepare_databases")
class TestTableFilter:
    """Group of tests for table-filter option"""

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("table_filter", ["index < 100"])
    def test_simple_table_diff_with_filter(self, cli, capsys, table_name, table_filter):
        """Test table diff with filter when no differences exist"""

        expected_total_rows_checked = 297
        cli.table_diff_cli("eqn-t9da", table_name, table_filter=table_filter)
        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"total rows checked\s*=\s*(\d+)", clean_output.lower())
        assert match, "Total rows checked not found in output"
        total_rows_checked = int(match.group(1))

        # Check that tables match
        assert (
            "tables match ok" in clean_output.lower()
        ), f"Table diff failed. Output: {output}"

        # Check that only filtered rows were processed
        assert (
            total_rows_checked == expected_total_rows_checked
        ), "Incorrect total rows processed"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("table_filter", ["index < 100"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_filter_and_differences(
        self,
        cli,
        capsys,
        table_name,
        table_filter,
        column_name,
        key_column,
        diff_file_path,
    ):
        """Test table diff with filter when differences exist within filter range"""
        try:
            # Introduce differences only within the filter range
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
            cur.execute(
                f"""
                UPDATE customers
                SET {column_name} = {column_name} || '-modified'
                WHERE index < 50
                RETURNING index, {column_name}
            """
            )
            conn.commit()
            cur.close()
            conn.close()

            expected_total_rows_checked = 297

            # Run table-diff with filter
            cli.table_diff_cli("eqn-t9da", table_name, table_filter=table_filter)
            captured = capsys.readouterr()
            output = captured.out

            clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
            match = re.search(r"total rows checked\s*=\s*(\d+)", clean_output.lower())
            assert match, "Total rows checked not found in output"
            total_rows_checked = int(match.group(1))

            # Verify output shows correct number of processed rows
            assert (
                total_rows_checked == expected_total_rows_checked
            ), "Did not process expected number of rows"

            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify all differences are within filter range
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 49
            ), "Expected 49 differences,"
            f" found {len(diff_data['diffs']['n1/n2']['n2'])}"
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                assert (
                    diff["index"] < 100
                ), f"Found diff outside filter range: index = {diff['index']}"

                assert diff[column_name].endswith(
                    "-modified"
                ), "Modified row doesn't have expected value"

        except Exception as e:
            pytest.fail(f"Failed to test differences with filter: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("table_filter", ["index >= 100"])
    def test_table_diff_with_filter_excluding_differences(
        self, cli, capsys, table_name, table_filter
    ):
        """Test table diff with filter that excludes the differences"""
        try:
            # Differences from previous test should still exist in index < 100
            # Run table-diff with filter that excludes those rows
            cli.table_diff_cli("eqn-t9da", table_name, table_filter=table_filter)
            captured = capsys.readouterr()
            output = captured.out
            expected_total_rows_checked = 29703  # 9901 x 3

            clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
            match = re.search(r"total rows checked\s*=\s*(\d+)", clean_output.lower())
            assert match, "Total rows checked not found in output"
            total_rows_checked = int(match.group(1))

            # Should report no differences since modified rows are outside filter
            assert (
                "tables match ok" in clean_output.lower()
            ), "Should not find differences outside filter range"

            # Verify correct number of rows processed
            assert (
                total_rows_checked == expected_total_rows_checked
            ), "Did not process expected number of rows"

        except Exception as e:
            pytest.fail(f"Failed to test filter excluding differences: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("table_filter", ["index < 100"])
    def test_table_repair_with_filter(
        self, cli, capsys, table_name, table_filter, diff_file_path
    ):
        """Test table repair with filter"""
        # Run repair with the same filter
        cli.table_repair_cli(
            "eqn-t9da",
            table_name,
            diff_file_path.path,
            source_of_truth="n1",
        )

        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)

        assert (
            "successfully applied diffs" in clean_output.lower()
        ), f"Table repair failed. Output: {output}"

        # Verify repair worked within filter range
        cli.table_diff_cli("eqn-t9da", table_name, table_filter=table_filter)
        captured = capsys.readouterr()
        output = captured.out
        assert (
            "tables match ok" in output.lower()
        ), "Tables don't match after repair within filter"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("table_filter", ["index < 100"])
    def test_table_rerun_with_filter(
        self, cli, capsys, table_name, table_filter, diff_file_path
    ):
        """Test table rerun with filter"""
        # First introduce new differences within filter range
        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
            cur.execute(
                """
                UPDATE customers
                SET city = 'FilterCity'
                WHERE index < 50
            """
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Failed to introduce diffs for rerun test: {str(e)}")

        # Get diff file with filter
        cli.table_diff_cli("eqn-t9da", table_name, table_filter=table_filter)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        path = match.group(1)

        cli.table_rerun_cli(
            "eqn-t9da",
            path,
            table_name,
            "demo",
            False,
        )
        captured = capsys.readouterr()
        output = captured.out
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)

        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        assert "written out to" in clean_output.lower(), "Table rerun failed"

        # Verify diffs are correct
        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        assert len(diff_data["diffs"]["n1/n2"]["n2"]) == 49, "Expected 49 differences"
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            assert diff["index"] < 100, "Found diff outside filter range"
            assert diff["city"] == "FilterCity", "Unexpected city value"
