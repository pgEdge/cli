import os
import sys
import pytest
import importlib.util
import psycopg
import concurrent.futures

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


@pytest.fixture(scope="session")
def prepare_databases(nodes):
    """Setup fixture that prepares all databases before running tests"""

    def prepare_node(node):

        # Our table definitions
        customers_sql = """
        CREATE TABLE IF NOT EXISTS customers (
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

        bytea_sql = """
        CREATE TABLE IF NOT EXISTS bytea_test (
            id SERIAL PRIMARY KEY,
            data bytea
        );
        """

        uuid_sql = """
        CREATE TABLE IF NOT EXISTS uuid_test (
            id UUID PRIMARY KEY,
            data int
        );
        """

        try:
            # Get connection for node using ace_core
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            cur = conn.cursor()

            # Creating the tables first
            cur.execute(customers_sql)
            cur.execute(bytea_sql)
            cur.execute(uuid_sql)

            # Loading the data
            with open(config.CUSTOMERS_CSV, "r") as f:
                with cur.copy(
                    "COPY customers FROM STDIN CSV HEADER DELIMITER ','"
                ) as copy:
                    copy.write(f.read())

            # Generate 100kb of random binary data
            binary_data = os.urandom(100 * 1024)  # 100kb of random bytes

            # Insert the binary data into bytea_test table
            cur.execute("INSERT INTO bytea_test (data) VALUES (%s)", (binary_data,))

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


@pytest.mark.usefixtures("prepare_databases")
def test_database_connectivity(nodes):
    """Test that we can connect to all prepared databases"""
    for node in nodes:
        try:
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            assert conn is not None
            conn.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to node {node}: {str(e)}")


@pytest.mark.usefixtures("prepare_databases")
def test_simple_table_diff(cli, capsys):
    """Test table diff on cluster eqn-t9da for public.customers table"""
    # Execute table diff
    cli.table_diff_cli("eqn-t9da", "public.customers")

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check for expected message
    assert "tables match ok" in output.lower(), f"Table diff failed. Output: {output}"


@pytest.fixture(scope="session", autouse=True)
def cleanup_databases(prepare_databases):
    """Cleanup fixture that cleans up all databases after running tests"""
    # Yield to let the tests run first
    yield

    # Cleanup code that runs after all tests complete
    drop_customers_sql = "DROP TABLE IF EXISTS customers;"
    drop_bytea_sql = "DROP TABLE IF EXISTS bytea_test;"
    drop_uuid_sql = "DROP TABLE IF EXISTS uuid_test;"

    nodes = prepare_databases  # prepare_databases returns the nodes list
    for node in nodes:
        try:
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute(drop_customers_sql)
            cur.execute(drop_bytea_sql)
            cur.execute(drop_uuid_sql)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Failed to cleanup node {node}: {str(e)}")
