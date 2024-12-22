import pytest
import psycopg
import json
import re
from test_simple import TestSimple


@pytest.mark.usefixtures("prepare_databases", "setup_datatypes")
class TestDataTypes(TestSimple):
    """Group of tests for various PostgreSQL data types"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_datatypes(self, nodes):
        """Setup fixture to create and populate a table with various data types"""
        try:
            # Create table with various data types on all nodes
            for node in nodes:
                print(f"Setting up datatypes test table on node {node}")
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Create the table with various data types
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS datatypes_test (
                        id UUID PRIMARY KEY,
                        int_col INTEGER,
                        float_col DOUBLE PRECISION,
                        array_col INTEGER[],
                        json_col JSONB,
                        bytea_col BYTEA,
                        point_col POINT,
                        text_col TEXT
                    )
                """
                )

                # Insert sample data
                cur.execute(
                    """
                    INSERT INTO datatypes_test VALUES
                    (
                        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
                        42,
                        3.14159,
                        ARRAY[1, 2, 3, 4, 5],
                        '{"key": "value", "nested": {"foo": "bar"}}',
                        decode('DEADBEEF', 'hex'),
                        point(1.5, 2.5),
                        'sample text'
                    ),
                    (
                        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
                        100,
                        2.71828,
                        ARRAY[10, 20, 30],
                        '{"numbers": [1, 2, 3], "active": true}',
                        decode('BADDCAFE', 'hex'),
                        point(3.7, 4.2),
                        'another sample'
                    ),
                    (
                        'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
                        -17,
                        0.577216,
                        ARRAY[]::INTEGER[],
                        '{"empty": true}',
                        NULL,
                        point(0, 0),
                        'third sample'
                    )
                """
                )

                conn.commit()
                cur.close()
                conn.close()

            yield  # Let the tests run

            # Cleanup: drop the test table
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute("DROP TABLE IF EXISTS datatypes_test")
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup datatypes test: {str(e)}")

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
        ],
    )
    @pytest.mark.parametrize("key_column", ["id"])
    def test_table_diff_with_differences(
        self,
        cli,
        capsys,
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
        ],
    )
    def test_table_rerun_temptable(
        self,
        cli,
        capsys,
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
