from datetime import datetime, timedelta, date, time
from decimal import Decimal
from ipaddress import IPv4Address
import pytest
import psycopg
import json
import re
from test_simple import TestSimple


@pytest.mark.usefixtures("prepare_databases")
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
                        text_col TEXT,
                        text_array_col TEXT[],
                        bool_col BOOLEAN,
                        bigint_col BIGINT,
                        smallint_col SMALLINT,
                        numeric_col NUMERIC(10, 4),
                        real_col REAL,
                        time_col TIME,
                        date_col DATE,
                        timestamp_col TIMESTAMP,
                        interval_col INTERVAL,
                        inet_col INET,
                        macaddr_col MACADDR,
                        money_col MONEY
                    )
                """
                )

                # Insert sample data
                self._insert_initial_data(cur)

                repset_add_datatypes_sql = """
                SELECT spock.repset_add_table('test_repset', 'datatypes_test')
                """
                cur.execute(repset_add_datatypes_sql)
                print("add datatypes to test_repset", cur.fetchone())

                conn.commit()
                cur.close()
                conn.close()

            yield  # Let the tests run

            # Cleanup: drop the test table
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                repset_remove_datatypes = """
                SELECT spock.repset_remove_table('test_repset', 'datatypes_test')
                """
                cur.execute(repset_remove_datatypes)
                print("remove datatypes from test_repset", cur.fetchone())

                cur.execute("DROP TABLE IF EXISTS datatypes_test CASCADE")
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup datatypes test: {str(e)}")

    def _insert_initial_data(self, cur):
        """Helper method to insert the initial dataset."""
        cur.execute(self._get_initial_data_sql())

    def _get_initial_data_sql(self):
        """Returns the SQL for inserting the initial dataset."""
        return """
            INSERT INTO datatypes_test VALUES
            (
                'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
                42,
                3.14159,
                ARRAY[1, 2, 3, 4, 5],
                '{"key": "value", "nested": {"foo": "bar"}}',
                decode('DEADBEEF', 'hex'),
                point(1.5, 2.5),
                'sample text',
                ARRAY['apple', 'banana', 'cherry'],
                true,
                9223372036854775807,
                32767,
                12345.6789,
                123.456,
                '12:34:56',
                '2024-01-01',
                '2024-01-01 12:34:56',
                '30 days',
                '192.168.1.1',
                '08:00:2b:01:02:03',
                12345.67
            ),
            (
                'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
                100,
                2.71828,
                ARRAY[10, 20, 30],
                '{"numbers": [1, 2, 3], "active": true}',
                decode('BADDCAFE', 'hex'),
                point(3.7, 4.2),
                'another sample',
                ARRAY['dog', 'cat', 'bird'],
                false,
                -9223372036854775808,
                -32768,
                -12345.6789,
                -123.456,
                '23:59:59',
                '2023-12-31',
                '2023-12-31 23:59:59',
                '-5 days',
                '10.0.0.1',
                '00:1A:2B:3C:4D:5E',
                -12345.67
            ),
            (
                'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
                -17,
                0.577216,
                ARRAY[]::INTEGER[],
                '{"empty": true}',
                NULL,
                point(0, 0),
                'third sample',
                ARRAY[]::TEXT[],
                true,
                0,
                0,
                0,
                0,
                '00:00:00',
                '1970-01-01',
                '1970-01-01 00:00:00',
                '0 seconds',
                '0.0.0.0',
                '00:00:00:00:00:00',
                0
            ),
            (
                'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14',
                NULL,
                NULL,
                ARRAY[NULL, 1, NULL],
                NULL,
                NULL,
                NULL,
                'null',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            ),
            (
                'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15',
                1,
                'NaN',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            )
        """

    def reset_data(self, nodes):
        """Reset data in the test table before each test function."""
        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute("TRUNCATE TABLE datatypes_test")
                self._insert_initial_data(cur)
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            pytest.fail(f"Failed to reset data between tests: {str(e)}")

    # Override the table_name parameter for all parameterized tests
    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        return super().test_simple_table_diff(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize(
        "column_name,test_value,expected_diffs",
        [
            ("int_col", "9999", 5),
            ("float_col", "123.456", 5),
            ("array_col", "ARRAY[99, 98, 97]", 5),
            ("json_col", '\'{"test": "modified"}\'', 5),
            ("bytea_col", "decode('FEEDFACE', 'hex')", 5),
            ("point_col", "point(99.9, 99.9)", 5),
            ("text_col", "'modified-text'", 5),
            ("text_array_col", "ARRAY['modified', 'text', 'array']", 5),
            ("bool_col", "false", 5),
            ("bigint_col", "1234567890123456789", 5),
            ("smallint_col", "-32768", 5),
            ("numeric_col", "98765.4321", 5),
            ("real_col", "987.654", 5),
            ("time_col", "'11:22:33'", 5),
            ("date_col", "'2025-05-25'", 5),
            ("timestamp_col", "'2025-05-25 11:22:33'", 5),
            ("interval_col", "'90 days'", 5),
            ("inet_col", "'192.168.100.200'", 5),
            ("macaddr_col", "'01:23:45:67:89:ab'", 5),
            ("money_col", "9876.54", 5),
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
        expected_diffs,
        key_column,
        diff_file_path,
    ):
        """Test table diff with differences for each data type"""
        try:
            # Introduce differences using spock.repair_mode(true)
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()

            cur.execute("SELECT spock.repair_mode(true)")
            # Get random rows to modify
            cur.execute(
                f"""
                UPDATE datatypes_test
                SET {column_name} = {test_value}
                WHERE id IN (SELECT id FROM datatypes_test)
                RETURNING id
            """
            )

            conn.commit()
            cur.close()
            conn.close()

            # Execute table diff and verify results
            cli.table_diff(
                cluster_name="eqn-t9da",
                table_name=table_name,
            )

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
                len(diff_data["diffs"]["n1/n2"]["n2"]) == expected_diffs
            ), f"Expected {expected_diffs} differences,"
            f" found {len(diff_data['diffs']['n1/n2']['n2'])}"

            # Verify the differences are correctly reported
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                diff_val = diff[column_name]
                expected_val_str = test_value.strip("'")

                if column_name == "json_col":
                    assert (
                        diff_val.get("test") == "modified"
                    ), f"Modified row {diff['id']} doesn't have expected JSON value"
                elif column_name == "array_col":
                    assert diff_val == [
                        99,
                        98,
                        97,
                    ], f"Modified row {diff['id']} doesn't have expected array value"
                elif column_name == "text_array_col":
                    assert diff_val == [
                        "modified",
                        "text",
                        "array",
                    ], (
                        f"Modified row {diff['id']} doesn't have expected text"
                        " array value"
                    )
                elif column_name == "point_col":
                    assert (
                        diff_val == "(99.9,99.9)"
                    ), f"Modified row {diff['id']} doesn't have expected point value"
                elif column_name == "bytea_col":
                    assert (
                        diff_val == "feedface"
                    ), f"Modified row {diff['id']} doesn't have expected bytea value"
                elif column_name == "macaddr_col":
                    assert (
                        diff_val == "01:23:45:67:89:ab"
                    ), f"Modified row {diff['id']} doesn't have expected macaddr value"
                elif column_name == "money_col":
                    cleaned_diff = diff_val.replace("$", "").replace(",", "")
                    assert float(cleaned_diff) == float(
                        expected_val_str
                    ), f"Modified row {diff['id']} doesn't have expected money value"
                elif column_name == "bool_col":
                    assert str(diff_val).lower() == expected_val_str.lower(), (
                        f"Modified row {diff['id']} "
                        "doesn't have expected boolean value"
                    )
                elif column_name == "interval_col":
                    # Interval representation can vary, so we check equality
                    # directly in Postgres
                    conn = psycopg.connect(host="n1", dbname="demo", user="admin")
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT %s::interval = %s::interval",
                        (str(diff_val), expected_val_str),
                    )
                    is_equal = cur.fetchone()[0]
                    cur.close()
                    conn.close()
                    assert is_equal, (
                        f"Modified row {diff['id']} "
                        f"doesn't have expected interval value. "
                        f"Got {diff_val}, expected equivalence to {expected_val_str}"
                    )
                else:
                    assert str(diff_val) == expected_val_str, (
                        f"Modified row {diff['id']} "
                        f"doesn't have expected value, got {diff_val} "
                        f"expected {expected_val_str}"
                    )

        except Exception as e:
            pytest.fail(f"Failed to test differences for {column_name}: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        return super().test_simple_table_repair(cli, capsys, table_name, diff_file_path)

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize("key_column", ["id"])
    @pytest.mark.parametrize(
        "column_name,test_value,expected_rerun_diffs",
        [
            ("int_col", "1234", 5),
            ("float_col", "98.765", 5),
            ("array_col", "ARRAY[11, 22, 33]", 5),
            ("json_col", '\'{"rerun": "modified"}\'', 5),
            ("bytea_col", "decode('ABCDEF12', 'hex')", 5),
            ("point_col", "point(88.8, 88.8)", 5),
            ("text_col", "'rerun-modified'", 5),
            ("text_array_col", "ARRAY['rerun', 'modified', 'array']", 5),
            ("bool_col", "true", 5),
            ("bigint_col", "-1234567890123456789", 5),
            ("smallint_col", "32767", 5),
            ("numeric_col", "-98765.4321", 5),
            ("real_col", "-987.654", 5),
            ("time_col", "'01:02:03'", 5),
            ("date_col", "'2022-02-02'", 5),
            ("timestamp_col", "'2022-02-02 01:02:03'", 5),
            ("interval_col", "'60 days'", 5),
            ("inet_col", "'127.0.0.1'", 5),
            ("macaddr_col", "'fe:dc:ba:98:76:54'", 5),
            ("money_col", "-9876.54", 5),
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
        expected_rerun_diffs,
        diff_file_path,
    ):
        """Test table rerun temptable with various data types"""
        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
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
        cli.table_diff(
            cluster_name="eqn-t9da",
            table_name=table_name,
        )
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        path = match.group(1)

        # Run table-rerun with hostdb behavior
        cli.table_rerun(
            cluster_name="eqn-t9da",
            diff_file=path,
            table_name=table_name,
            dbname="demo",
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
            len(diff_data["diffs"]["n1/n2"]["n2"]) == expected_rerun_diffs
        ), f"Expected {expected_rerun_diffs} differences, "
        f"found {len(diff_data['diffs']['n1/n2']['n2'])}"

        # Verify the differences are correctly reported
        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            diff_val = diff[column_name]
            expected_val_str = test_value.strip("'")

            if column_name == "json_col":
                assert (
                    diff_val.get("rerun") == "modified"
                ), f"Modified row {diff['id']} doesn't have expected JSON value"
            elif column_name == "array_col":
                assert diff_val == [
                    11,
                    22,
                    33,
                ], f"Modified row {diff['id']} doesn't have expected array value"
            elif column_name == "text_array_col":
                assert diff_val == [
                    "rerun",
                    "modified",
                    "array",
                ], f"Modified row {diff['id']} doesn't have expected text array value"
            elif column_name == "point_col":
                assert (
                    diff_val == "(88.8,88.8)"
                ), f"Modified row {diff['id']} doesn't have expected point value"
            elif column_name == "bytea_col":
                assert (
                    diff_val == "abcdef12"
                ), f"Modified row {diff['id']} doesn't have expected bytea value"
            elif column_name == "macaddr_col":
                assert (
                    diff_val == "fe:dc:ba:98:76:54"
                ), f"Modified row {diff['id']} doesn't have expected macaddr value"
            elif column_name == "money_col":
                cleaned_diff = diff_val.replace("$", "").replace(",", "")
                assert float(cleaned_diff) == float(
                    expected_val_str
                ), f"Modified row {diff['id']} doesn't have expected money value"
            elif column_name == "bool_col":
                assert (
                    str(diff_val).lower() == expected_val_str.lower()
                ), f"Modified row {diff['id']} doesn't have expected boolean value"
            elif column_name == "interval_col":
                # Interval representation can vary, so we check equality in the DB
                conn = psycopg.connect(host="n1", dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute(
                    "SELECT %s::interval = %s::interval",
                    (str(diff_val), expected_val_str),
                )
                is_equal = cur.fetchone()[0]
                cur.close()
                conn.close()
                assert is_equal, (
                    f"Modified row {diff['id']} "
                    f"doesn't have expected interval value. "
                    f"Got {diff_val}, expected equivalence to {expected_val_str}"
                )
            else:
                assert str(diff_val) == expected_val_str, (
                    f"Modified row {diff['id']} "
                    f"doesn't have expected value, got {diff_val} "
                    f"expected {expected_val_str}"
                )

    def _verify_repaired_value(self, column_name, repaired_value, expected_value):
        """Helper function to verify repaired values based on data type"""
        if column_name == "bytea_col":
            assert (
                repaired_value == expected_value
            ), "Repaired bytea value doesn't match expected value"
        elif column_name == "point_col":
            if isinstance(repaired_value, str):
                repaired_tuple = tuple(
                    map(float, repaired_value.strip("()").split(","))
                )
            else:
                repaired_tuple = repaired_value

            expected_tuple = tuple(map(float, expected_value.strip("()").split(",")))
            assert (
                repaired_tuple == expected_tuple
            ), "Repaired point value doesn't match expected value"
        elif column_name == "numeric_col":
            assert repaired_value == Decimal(
                expected_value
            ), f"Repaired value for {column_name} doesn't match"
        elif column_name == "inet_col":
            assert repaired_value == IPv4Address(
                expected_value
            ), f"Repaired value for {column_name} doesn't match"
        elif column_name in ["time_col", "date_col", "timestamp_col", "interval_col"]:
            assert (
                repaired_value == expected_value
            ), f"Repaired value for {column_name} doesn't match"
        elif column_name == "money_col":
            cleaned_repaired = str(repaired_value).replace("$", "").replace(",", "")
            cleaned_expected = str(expected_value).replace("$", "").replace(",", "")
            assert float(cleaned_repaired) == float(
                cleaned_expected
            ), f"Repaired money value doesn't match for {column_name}"
        else:
            assert (
                repaired_value == expected_value
            ), f"Repaired value doesn't match expected value for {column_name}"

    @pytest.mark.parametrize("table_name", ["public.datatypes_test"])
    @pytest.mark.parametrize(
        "column_name,test_value,expected_value",
        [
            ("int_col", "9999", 9999),
            ("float_col", "123.456", 123.456),
            ("array_col", "ARRAY[99, 98, 97]", [99, 98, 97]),
            ("json_col", '\'{"test": "modified"}\'', {"test": "modified"}),
            ("bytea_col", "decode('FEEDFACE', 'hex')", b"\xfe\xed\xfa\xce"),
            ("point_col", "point(99.9, 99.9)", "(99.9,99.9)"),
            ("text_col", "'modified-text'", "modified-text"),
            (
                "text_array_col",
                "ARRAY['modified', 'text', 'array']",
                ["modified", "text", "array"],
            ),
            ("bool_col", "false", False),
            ("bigint_col", "1234567890123456789", 1234567890123456789),
            ("smallint_col", "-32768", -32768),
            ("numeric_col", "98765.4321", Decimal("98765.4321")),
            ("real_col", "987.654", 987.654),
            ("time_col", "'11:22:33'", time(11, 22, 33)),
            ("date_col", "'2025-05-25'", date(2025, 5, 25)),
            (
                "timestamp_col",
                "'2025-05-25 11:22:33'",
                datetime(2025, 5, 25, 11, 22, 33),
            ),
            ("interval_col", "'90 days'", timedelta(days=90)),
            ("inet_col", "'192.168.100.200'", "192.168.100.200"),
            ("macaddr_col", "'01:23:45:67:89:ab'", "01:23:45:67:89:ab"),
            ("money_col", "9876.54", "$9,876.54"),
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
            cur.execute("SELECT spock.repair_mode(true)")
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
            cli.table_diff(
                cluster_name="eqn-t9da",
                table_name=table_name,
            )
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Run table-repair using n2 as source of truth
            cli.table_repair(
                cluster_name="eqn-t9da",
                table_name=table_name,
                diff_file=diff_file_path.path,
                source_of_truth="n2",
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
            self._verify_repaired_value(column_name, repaired_value, expected_value)

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("id_to_update", ["d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"])
    def test_null_and_string_literal_handling(
        self, cli, capsys, diff_file_path, id_to_update
    ):
        """
        Verify that NULL values and string literals like 'null' are
        handled correctly.
        """
        try:
            # Our prior repair unfortunately reset a lot of fields, so we reset
            # the data first here
            self.reset_data(nodes=["n1", "n2"])

            # On n2, update text_col from 'null' to 'not null' and
            # int_col from NULL to a number
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
            # This specific id has "null" as a literal in the text_col
            cur.execute(
                """
                UPDATE datatypes_test
                SET text_col = 'not null anymore', int_col = 123
                WHERE id = %s
                """,
                (id_to_update,),
            )
            conn.commit()
            cur.close()
            conn.close()

            # Run table-diff
            cli.table_diff(cluster_name="eqn-t9da", table_name="public.datatypes_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Verify diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            diffs_n1 = diff_data["diffs"]["n1/n2"]["n1"]
            diffs_n2 = diff_data["diffs"]["n1/n2"]["n2"]

            assert len(diffs_n1) == 1, "Expected 1 difference on n1"
            assert len(diffs_n2) == 1, "Expected 1 difference on n2"

            # Check n1 (original values)
            assert diffs_n1[0]["id"] == id_to_update
            assert diffs_n1[0]["text_col"] == "null"
            assert diffs_n1[0]["int_col"] is None

            # Check n2 (modified values)
            assert diffs_n2[0]["id"] == id_to_update
            assert diffs_n2[0]["text_col"] == "not null anymore"
            assert diffs_n2[0]["int_col"] == 123

            # Run table-repair
            cli.table_repair(
                cluster_name="eqn-t9da",
                table_name="public.datatypes_test",
                diff_file=diff_file_path.path,
                source_of_truth="n2",
            )

            # Verify repair on n1
            conn = psycopg.connect(host="n1", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                """
                SELECT text_col, int_col FROM datatypes_test
                WHERE id = %s
                """,
                (id_to_update,),
            )
            repaired_text, repaired_int = cur.fetchone()
            cur.close()
            conn.close()

            assert repaired_text == "not null anymore"
            assert repaired_int == 123

        except Exception as e:
            pytest.fail(f"Test for null handling failed: {str(e)}")

    @pytest.mark.parametrize("id_to_update", ["e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"])
    def test_ast_literal_eval_fallback(self, cli, capsys, diff_file_path, id_to_update):
        """
        Verify that the fallback to string representation works when
        ast.literal_eval fails.
        """
        try:
            # Resetting again here
            self.reset_data(nodes=["n1", "n2"])

            # On n2, update float_col from NaN to a valid number
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
            cur.execute(
                """
                UPDATE datatypes_test
                SET float_col = 1.23
                WHERE id = %s
                """,
                (id_to_update,),
            )
            conn.commit()
            cur.close()
            conn.close()

            # Run table-diff
            cli.table_diff(cluster_name="eqn-t9da", table_name="public.datatypes_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            # Verify diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            diffs_n1 = diff_data["diffs"]["n1/n2"]["n1"]
            diffs_n2 = diff_data["diffs"]["n1/n2"]["n2"]

            assert len(diffs_n1) == 1, "Expected 1 difference on n1"
            assert len(diffs_n2) == 1, "Expected 1 difference on n2"

            # Check n1 (original 'NaN' value)
            assert diffs_n1[0]["id"] == id_to_update
            assert diffs_n1[0]["float_col"] == "nan"

            # Check n2 (modified value)
            assert diffs_n2[0]["id"] == id_to_update
            assert diffs_n2[0]["float_col"] == 1.23

            # Run table-repair
            cli.table_repair(
                cluster_name="eqn-t9da",
                table_name="public.datatypes_test",
                diff_file=diff_file_path.path,
                source_of_truth="n2",
            )

            # Verify repair on n1
            conn = psycopg.connect(host="n1", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(
                """
                SELECT float_col FROM datatypes_test
                WHERE id = %s
                """,
                (id_to_update,),
            )
            repaired_float = cur.fetchone()[0]
            cur.close()
            conn.close()

            assert repaired_float == 1.23

        except Exception as e:
            pytest.fail(f"Test for ast.literal_eval fallback failed: {str(e)}")
