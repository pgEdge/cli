import os
import sys
import pytest
import importlib.util
import psycopg
import concurrent.futures
import json
import re

import test_config as config

# Sets Environment Variables for Commands
os.environ["MY_HOME"] = config.PGEDGE_HOME
os.environ["MY_LOGS"] = os.path.join(config.PGEDGE_HOME, "data", "logs", "cli_log.out")
os.environ["MY_LITE"] = os.path.join(config.PGEDGE_HOME, "data", "conf", "db_local.db")
os.environ["MY_CMD"] = "pgedge"


# Loads a module as a callable object
def load_mod(mod: str):
    try:
        script_dir = os.path.join("hub", "scripts")
        ace_path = os.path.join(script_dir, f"{mod}.py")
        ace_dir = os.path.dirname(ace_path)
        sys.path.insert(0, ace_dir)

        spec = importlib.util.spec_from_file_location(mod, ace_path)
        ace = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ace)
        sys.path.pop(0)

        return ace

    except Exception as e:
        print(f"Error: loading {mod}: {e}")
        exit(1)


@pytest.fixture(scope="session", autouse=True)
def set_run_dir():
    os.chdir(config.PGEDGE_HOME)


# Global fixtures
@pytest.fixture(scope="session")
def cli():
    return load_mod("ace_cli")


@pytest.fixture(scope="session")
def core():
    return load_mod("ace_core")


@pytest.fixture(scope="session")
def nodes():
    return ["n1", "n2", "n3"]


@pytest.fixture(scope="class")
def diff_file_path():
    """Fixture to store and share the diff file path between tests"""

    class DiffPathHolder:
        path = None

    return DiffPathHolder


@pytest.fixture(scope="session")
def prepare_databases(nodes):
    """Setup fixture that prepares all databases before running tests"""

    def prepare_node(node):

        # Our table definitions
        customers_sql = """
        CREATE TABLE customers (
            index INTEGER PRIMARY KEY NOT NULL,
            customer_id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            phone_1 TEXT NOT NULL,
            phone_2 TEXT NOT NULL,
            email TEXT NOT NULL,
            subscription_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            website TEXT NOT NULL
        );
        """

        try:
            # Get connection for node using ace_core
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            cur = conn.cursor()

            # Creating the tables first
            cur.execute(customers_sql)

            # Loading the data
            with open(config.CUSTOMERS_CSV, "r") as f:
                with cur.copy(
                    "COPY customers FROM STDIN CSV HEADER DELIMITER ','"
                ) as copy:
                    copy.write(f.read())

            conn.commit()

            print(f"Successfully prepared database on node {node}")

            # Clean up
            cur.close()
            conn.close()
            return True

        except Exception as e:
            print(f"Error executing SQL on node {node}: {str(e)}")
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(nodes)) as executor:
        results = list(executor.map(prepare_node, nodes))

    # If database setup fails, we should fail the entire test suite
    if not all(results):
        pytest.fail("Database preparation failed")

    # Return the nodes for use in tests
    return nodes


@pytest.fixture(scope="session", autouse=True)
def cleanup_databases(prepare_databases):
    """Cleanup all databases after running tests"""
    # Yield to let the tests run first
    yield

    # Cleanup code that runs after all tests complete
    drop_customers_sql = "DROP TABLE IF EXISTS customers CASCADE;"

    # prepare_databases returns the nodes list
    nodes = prepare_databases

    for node in nodes:
        try:
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(drop_customers_sql)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Failed to cleanup node {node}: {str(e)}")


@pytest.mark.usefixtures("prepare_databases")
class TestSimple:
    """Group of tests for simple ACE operations"""

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def _introduce_differences(self, node, table_name, column_name, key_column):
        """Helper method to introduce differences in a table

        Args:
            node: The node to introduce differences on
            table_name: The table name (with schema)
            column_name: The column to modify (default: "first_name")

        Returns:
            Set of modified row indices
        """
        conn = psycopg.connect(host=node, dbname="demo", user="admin")
        cur = conn.cursor()

        # Note: column_name should be quoted if it contains uppercase
        cur.execute(
            f"""
            WITH random_rows AS (
                SELECT \"{key_column}\"
                FROM {table_name.split('.')[0]}.\"{table_name.split('.')[1]}\"
                ORDER BY random()
                LIMIT 50
            )
            UPDATE {table_name.split('.')[0]}.\"{table_name.split('.')[1]}\"
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

    def test_database_connectivity(self, nodes):
        """Test that we can connect to all prepared databases"""
        for node in nodes:
            try:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
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
        self, cli, capsys, table_name, column_name, key_column
    ):
        """Test table diff when differences exist between nodes"""
        try:
            # Introduce differences using the helper method
            modified_indices = self._introduce_differences(
                "n2", table_name, column_name, key_column
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
                len(diff_data["n1/n2"]["n2"]) == 50
            ), f"Expected 50 differences, but found {len(diff_data['n1/n2']['n2'])}"

            # Verify each modified row is present in the diff
            diff_indices = {
                diff[key_column] for diff in diff_data["n1/n2"]["n2"]
            }  # Set of indices from diff file

            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["n1/n2"]["n2"]:
                assert diff[column_name].endswith(
                    "-modified"
                ), f"Modified row {diff[key_column]} doesn't have expected suffix"

            # Verify the control rows are not modified
            for diff in diff_data["n1/n2"]["n1"]:
                assert not diff[column_name].endswith(
                    "-modified"
                ), f"Control row {diff[key_column]} shouldn't have modification suffix"

        except Exception as e:
            pytest.fail(f"Failed to introduce diffs: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name):
        """Test table repair on cluster eqn-t9da for specified table"""
        cli.table_repair_cli(
            "eqn-t9da",
            diff_file_path.path,
            "n1",
            table_name,
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
    def test_table_rerun_temptable(self, cli, capsys, table_name, key_column):
        """Test table rerun temptable on cluster eqn-t9da for specified table"""

        # We will start by introducing diffs to the customers table on n2

        schema, table = table_name.split(".")

        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
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
        assert len(diff_data["n1/n2"]["n2"]) == 100, "Expected 100 differences"

        for diff in diff_data["n1/n2"]["n2"]:
            assert diff["city"] == "Casablanca", "Expected city to be 'Casablanca'"

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name):
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
        assert len(diff_data["n1/n2"]["n2"]) == 100, "Expected 100 differences"

        # Verify the diffs are correct
        for diff in diff_data["n1/n2"]["n2"]:
            assert diff["city"] == "Casablanca", "Expected city to be 'Casablanca'"

        # Now that we have verified diffs through both methods, we can use repair
        # to restore the state of the table
        cli.table_repair_cli(
            "eqn-t9da",
            diff_file_path.path,
            "n1",
            table_name,
        )

        captured = capsys.readouterr()
        output = captured.out

        assert (
            "successfully applied diffs" in output.lower()
        ), f"Table repair failed. Output: {output}"


@pytest.mark.usefixtures("prepare_databases", "setup_mixed_case")
class TestMixedCaseNames(TestSimple):
    """Group of tests for mixed case table and column names"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_mixed_case(self, nodes):
        """Setup fixture to rename table and columns to mixed case before tests"""

        try:
            # Rename table and columns to mixed case on all nodes
            for node in nodes:
                print(f"Setting up mixed case on node {node}")
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # First rename the table
                cur.execute('ALTER TABLE customers RENAME TO "CuStOmErS"')

                # Then rename the columns
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN first_name TO "FiRsT_NaMe"
                """
                )
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN last_name TO "LaSt_NaMe"
                """
                )
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN subscription_date TO "SuBsCrIpTiOn_DaTe"
                """
                )

                conn.commit()
                cur.close()
                conn.close()

            yield  # Let the tests run

            # Cleanup: rename everything back to lowercase
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # First rename the columns back
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN "FiRsT_NaMe" TO first_name
                """
                )
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN "LaSt_NaMe" TO last_name
                """
                )
                cur.execute(
                    """
                    ALTER TABLE "CuStOmErS"
                    RENAME COLUMN "SuBsCrIpTiOn_DaTe" TO subscription_date
                """
                )

                # Then rename the table back
                cur.execute('ALTER TABLE "CuStOmErS" RENAME TO customers')

                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            pytest.fail(
                f"Failed to setup/cleanup mixed case table and columns: {str(e)}"
            )

    # Override the table_name parameter for all parameterised tests
    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        return super().test_simple_table_diff(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    @pytest.mark.parametrize("column_name", ["FiRsT_NaMe"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_differences(
        self, cli, capsys, table_name, column_name, key_column
    ):
        return super().test_table_diff_with_differences(
            cli, capsys, table_name, column_name, key_column
        )

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    def test_simple_table_repair(self, cli, capsys, table_name):
        return super().test_simple_table_repair(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(self, cli, capsys, table_name, key_column):
        return super().test_table_rerun_temptable(cli, capsys, table_name, key_column)

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name):
        return super().test_table_rerun_multiprocessing(cli, capsys, table_name)


@pytest.mark.usefixtures("prepare_databases", "setup_composite_keys")
class TestCompositeKeys(TestSimple):
    """Group of tests for composite primary keys"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_composite_keys(self, nodes):
        """Setup fixture to modify customers table to use composite primary keys"""
        try:
            # Modify table to use composite keys on all nodes
            for node in nodes:
                print(f"Setting up composite key on node {node}")
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Drop existing primary key and create composite key
                cur.execute(
                    """
                    ALTER TABLE customers
                    DROP CONSTRAINT customers_pkey;
                """
                )

                # Rename the key columns to mixed case
                cur.execute('ALTER TABLE customers RENAME COLUMN index TO "InDeX"')
                cur.execute(
                    'ALTER TABLE customers RENAME COLUMN customer_id TO "CuStOmEr_Id"'
                )

                # Add composite primary key
                cur.execute(
                    """
                    ALTER TABLE customers
                    ADD PRIMARY KEY ("InDeX", "CuStOmEr_Id");
                """
                )

                conn.commit()
                cur.close()
                conn.close()

            yield  # Let the tests run

            # Cleanup: restore original primary key
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Drop composite key
                cur.execute(
                    """
                    ALTER TABLE customers
                    DROP CONSTRAINT customers_pkey;
                """
                )

                # Rename columns back
                cur.execute('ALTER TABLE customers RENAME COLUMN "InDeX" TO index')
                cur.execute(
                    'ALTER TABLE customers RENAME COLUMN "CuStOmEr_Id" TO customer_id'
                )

                # Restore original primary key
                cur.execute(
                    """
                    ALTER TABLE customers
                    ADD PRIMARY KEY (index);
                """
                )

                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup composite key: {str(e)}")

    # Override the table_name parameter for all parameterized tests
    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        return super().test_simple_table_diff(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["InDeX"])
    def test_table_diff_with_differences(
        self, cli, capsys, table_name, column_name, key_column
    ):
        return super().test_table_diff_with_differences(
            cli, capsys, table_name, column_name, key_column
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name):
        return super().test_simple_table_repair(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["InDeX"])
    def test_table_rerun_temptable(self, cli, capsys, table_name, key_column):
        return super().test_table_rerun_temptable(cli, capsys, table_name, key_column)

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name):
        return super().test_table_rerun_multiprocessing(cli, capsys, table_name)


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
        self, cli, capsys, table_name, column_name, test_value, key_column
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
                len(diff_data["n1/n2"]["n2"]) == 3
            ), f"Expected 50 differences, found {len(diff_data['n1/n2']['n2'])}"

            # Verify modified rows are in diff
            diff_indices = {str(diff["id"]) for diff in diff_data["n1/n2"]["n2"]}
            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["n1/n2"]["n2"]:
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
    def test_simple_table_repair(self, cli, capsys, table_name):
        return super().test_simple_table_repair(cli, capsys, table_name)

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
        self, cli, capsys, table_name, key_column, column_name, test_value
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
            len(diff_data["n1/n2"]["n2"]) == 3
        ), f"Expected 3 differences, found {len(diff_data['n1/n2']['n2'])}"

        # Verify the differences are correctly reported
        for diff in diff_data["n1/n2"]["n2"]:
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
        self, cli, capsys, table_name, column_name, test_value
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
            len(diff_data["n1/n2"]["n2"]) == 3
        ), f"Expected 3 differences, found {len(diff_data['n1/n2']['n2'])}"

        # Verify the differences are correctly reported
        for diff in diff_data["n1/n2"]["n2"]:
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
        self, cli, capsys, table_name, table_filter, column_name, key_column
    ):
        """Test table diff with filter when differences exist within filter range"""
        try:
            # Introduce differences only within the filter range
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
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
                len(diff_data["n1/n2"]["n2"]) == 49
            ), f"Expected 49 differences, found {len(diff_data['n1/n2']['n2'])}"
            for diff in diff_data["n1/n2"]["n2"]:
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
    def test_table_repair_with_filter(self, cli, capsys, table_name, table_filter):
        """Test table repair with filter"""
        # Run repair with the same filter
        cli.table_repair_cli("eqn-t9da", diff_file_path.path, "n1", table_name)

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
    def test_table_rerun_with_filter(self, cli, capsys, table_name, table_filter):
        """Test table rerun with filter"""
        # First introduce new differences within filter range
        try:
            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
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

        # Test both rerun behaviors with filter
        for behavior in ["hostdb", "multiprocessing"]:
            cli.table_rerun_cli(
                "eqn-t9da",
                path,
                table_name,
                "demo",
                False,
                behavior,
            )
            captured = capsys.readouterr()
            output = captured.out
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output
            )

            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file_path.path = match.group(1)

            assert (
                "written out to" in clean_output.lower()
            ), f"Table rerun failed for {behavior}"

            # Verify diffs are correct
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            assert (
                len(diff_data["n1/n2"]["n2"]) == 49
            ), f"Expected 49 differences for {behavior}"
            for diff in diff_data["n1/n2"]["n2"]:
                assert (
                    diff["index"] < 100
                ), f"Found diff outside filter range in {behavior}"
                assert (
                    diff["city"] == "FilterCity"
                ), f"Unexpected city value in {behavior}"
