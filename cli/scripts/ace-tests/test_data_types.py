import pytest
import psycopg
import json
import re
from test_simple import TestSimple


@pytest.mark.usefixtures("prepare_databases")
class TestDataTypes(TestSimple):
    """Group of tests for various PostgreSQL data types"""

    # Override the table_name parameter for all parameterized tests
    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        return super().test_simple_table_diff(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize(
        "column_name,test_value",
        [
            ("int_col", "9999"),
            ("float_col", "123.456"),
            ("array_col", "ARRAY[99, 98, 97]"),
            ("json_col", '\'{"test": "modified"}\''),
            ("bytea_col", "decode('FEEDFACE', 'hex')"),
            ("point_col", "point(99.9, 99.9)"),
            ("text_col", "'modified-text'"),
            ("text_array_col", "ARRAY['modified', 'text', 'array']"),
        ],
    )
    @pytest.mark.parametrize("key_column", ["id"])
    def test_table_diff_with_differences(
        self,
        cli,
        capsys,
        ace_conf,
        table_name,
        column_name,
        test_value,
        key_column,
        diff_file_path,
    ):
        """Test table diff with differences for each data type"""
        try:
            # Introduce differences using SQL that works for any data type
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()

            # Get random rows to modify
            cur.execute(
                f"""
                UPDATE datatypes_test
                SET {column_name} = {test_value}
                WHERE id IN (SELECT id FROM datatypes_test)
                RETURNING id
            """
            )

            modified_rows = cur.fetchall()
            modified_indices = {
                str(row[0]) for row in modified_rows
            }  # Convert UUID to string

            conn.commit()
            cur.close()
            conn.close()

            # Execute table diff and verify results
            cli.table_diff_cli("eqn-t9da", table_name)

            # Capture and verify output
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )

            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Read and verify diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify number of differences
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 3
            ), "Expected 3 differences,"
            f" found {len(diff_data['diffs']['n1/n2']['n2'])}"

            # Verify modified rows are in diff
            diff_indices = {
                str(diff["id"]) for diff in diff_data["diffs"]["n1/n2"]["n2"]
            }
            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                if column_name == "json_col":
                    assert (
                        diff[column_name].get("test") == "modified"
                    ), f"Modified row {diff['id']} doesn't have expected JSON value"
                elif column_name == "array_col":
                    assert diff[column_name] == [
                        99,
                        98,
                        97,
                    ], f"Modified row {diff['id']} doesn't have expected array value"
                elif column_name == "text_array_col":
                    assert diff[column_name] == [
                        "modified",
                        "text",
                        "array",
                    ], (
                        f"Modified row {diff['id']} doesn't have expected "
                        "text array value"
                    )
                elif column_name == "point_col":
                    assert (
                        diff[column_name] == "(99.9,99.9)"
                    ), f"Modified row {diff['id']} doesn't have expected point value"
                elif column_name == "bytea_col":
                    print("bytea col: ", diff[column_name])
                    assert (
                        diff[column_name] == "feedface"
                    ), f"Modified row {diff['id']} doesn't have expected bytea value"
                else:
                    assert str(diff[column_name]) in (
                        test_value.strip("'"),
                        "9999",
                        "123.456",
                        "modified-text",
                    ), f"Modified row {diff['id']} doesn't have expected value"

        except Exception as e:
            pytest.fail(f"Failed to test differences for {column_name}: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        return super().test_simple_table_repair(cli, capsys, table_name, diff_file_path)

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize("key_column", ["id"])
    @pytest.mark.parametrize(
        "column_name,test_value",
        [
            ("int_col", "1234"),
            ("float_col", "98.765"),
            ("array_col", "ARRAY[11, 22, 33]"),
            ("json_col", '\'{"rerun": "modified"}\''),
            ("bytea_col", "decode('ABCDEF12', 'hex')"),
            ("point_col", "point(88.8, 88.8)"),
            ("text_col", "'rerun-modified'"),
            ("text_array_col", "ARRAY['rerun', 'modified', 'array']"),
        ],
    )
    def test_table_rerun_temptable(
        self,
        cli,
        capsys,
        ace_conf,
        table_name,
        key_column,
        column_name,
        test_value,
        diff_file_path,
    ):
        """Test table rerun temptable with various data types"""
        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE datatypes_test
                SET {column_name} = {test_value}
                WHERE id IN (
                    SELECT id
                    FROM datatypes_test
                )
            """
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Failed to introduce diffs on n2: {str(e)}")

        # Run table-diff to get the diff file
        cli.table_diff_cli("eqn-t9da", table_name)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        path = match.group(1)

        # Run table-rerun with hostdb behavior
        cli.table_rerun_cli("eqn-t9da", path, table_name, "demo", False, "hostdb")

        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        # Verify the diffs
        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        assert (
            len(diff_data["diffs"]["n1/n2"]["n2"]) == 3
        ), f"Expected 3 differences, found {len(diff_data['diffs']['n1/n2']['n2'])}"

        # Verify the differences are correctly reported
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            if column_name == "json_col":
                assert (
                    diff[column_name].get("rerun") == "modified"
                ), f"Modified row {diff['id']} doesn't have expected JSON value"
            elif column_name == "array_col":
                assert diff[column_name] == [
                    11,
                    22,
                    33,
                ], f"Modified row {diff['id']} doesn't have expected array value"
            elif column_name == "text_array_col":
                assert diff[column_name] == [
                    "rerun",
                    "modified",
                    "array",
                ], f"Modified row {diff['id']} doesn't have expected text array value"
            elif column_name == "point_col":
                assert (
                    diff[column_name] == "(88.8,88.8)"
                ), f"Modified row {diff['id']} doesn't have expected point value"
            elif column_name == "bytea_col":
                assert (
                    diff[column_name] == "abcdef12"
                ), f"Modified row {diff['id']} doesn't have expected bytea value"
            else:
                assert str(diff[column_name]) in (
                    test_value.strip("'"),
                    "1234",
                    "98.765",
                    "rerun-modified",
                ), f"Modified row {diff['id']} doesn't have expected value"

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize(
        "column_name,test_value",
        [
            ("int_col", "5678"),
            ("float_col", "76.543"),
            ("array_col", "ARRAY[44, 55, 66]"),
            ("json_col", '\'{"multiproc": "modified"}\''),
            ("bytea_col", "decode('98765432', 'hex')"),
            ("point_col", "point(77.7, 77.7)"),
            ("text_col", "'multiproc-modified'"),
            ("text_array_col", "ARRAY['multiproc', 'modified', 'array']"),
        ],
    )
    def test_table_rerun_multiprocessing(
        self,
        cli,
        capsys,
        table_name,
        column_name,
        test_value,
        diff_file_path,
    ):
        """Test table rerun multiprocessing with various data types"""

        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE datatypes_test
                SET {column_name} = {test_value}
                WHERE id IN (
                    SELECT id
                    FROM datatypes_test
                )
            """
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Failed to introduce diffs on n2: {str(e)}")

        # Run table-diff to get the diff file
        cli.table_diff_cli("eqn-t9da", table_name)
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
            "multiprocessing",
        )

        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        # Verify the diffs
        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        assert (
            len(diff_data["diffs"]["n1/n2"]["n2"]) == 3
        ), f"Expected 3 differences, found {len(diff_data['diffs']['n1/n2']['n2'])}"

        # Verify the differences are correctly reported
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            if column_name == "json_col":
                assert (
                    diff[column_name].get("multiproc") == "modified"
                ), f"Modified row {diff['id']} doesn't have expected JSON value"
            elif column_name == "array_col":
                assert diff[column_name] == [
                    44,
                    55,
                    66,
                ], f"Modified row {diff['id']} doesn't have expected array value"
            elif column_name == "text_array_col":
                assert diff[column_name] == [
                    "multiproc",
                    "modified",
                    "array",
                ], f"Modified row {diff['id']} doesn't have expected text array value"
            elif column_name == "point_col":
                assert (
                    diff[column_name] == "(77.7,77.7)"
                ), f"Modified row {diff['id']} doesn't have expected point value"
            elif column_name == "bytea_col":
                assert (
                    diff[column_name] == "98765432"
                ), f"Modified row {diff['id']} doesn't have expected bytea value"
            else:
                assert str(diff[column_name]) in (
                    test_value.strip("'"),
                    "5678",
                    "76.543",
                    "multiproc-modified",
                ), f"Modified row {diff['id']} doesn't have expected value"

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize(
        "column_name,test_value,expected_value",
        [
            ("int_col", "9999", 9999),
            ("float_col", "123.456", 123.456),
            ("array_col", "ARRAY[99, 98, 97]", [99, 98, 97]),
            ("json_col", '\'{"test": "modified"}\'', {"test": "modified"}),
            ("bytea_col", "decode('FEEDFACE', 'hex')", b'\xfe\xed\xfa\xce'),
            ("point_col", "point(99.9, 99.9)", "(99.9,99.9)"),
            ("text_col", "'modified-text'", "modified-text"),
            (
                "text_array_col",
                "ARRAY['modified', 'text', 'array']",
                ["modified", "text", "array"]
            ),
        ],
    )
    def test_table_repair_datatypes(
        self,
        cli,
        capsys,
        table_name,
        column_name,
        test_value,
        expected_value,
        diff_file_path,
    ):
        """Test table repair with various data types"""
        try:
            # First introduce differences on n2
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE datatypes_test
                SET {column_name} = {test_value}
                WHERE id IN (
                    SELECT id
                    FROM datatypes_test
                )
            """
            )
            conn.commit()
            cur.close()
            conn.close()

            # Run table-diff to get the diff file
            cli.table_diff_cli("eqn-t9da", table_name)
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
                "",
                captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Run table-repair using n2 as source of truth
            cli.table_repair_cli(
                "eqn-t9da",
                table_name,
                diff_file_path.path,
                source_of_truth="n2"
            )

            # Verify the repair worked by checking values on n1
            conn = psycopg.connect(host="n1", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                f"SELECT {column_name} FROM datatypes_test "
                "WHERE id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'"
            )
            repaired_value = cur.fetchone()[0]
            cur.close()
            conn.close()

            # Compare with expected value
            if column_name == "bytea_col":
                assert (
                    repaired_value == expected_value
                ), "Repaired bytea value doesn't match expected value"
            elif column_name == "point_col":
                assert (
                    str(repaired_value) == expected_value
                ), "Repaired point value doesn't match expected value"
            else:
                assert (
                    repaired_value == expected_value
                ), f"Repaired value doesn't match expected value for {column_name}"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
