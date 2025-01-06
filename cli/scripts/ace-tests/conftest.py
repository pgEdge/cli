# flake8: disable=unused-import

import concurrent.futures
import importlib.util
import os
import sys
import pytest
import psycopg
import test_config

# Set up paths
os.environ["PGEDGE_HOME"] = test_config.PGEDGE_HOME
sys.path.append(test_config.PGEDGE_HOME)
sys.path.append(os.path.join(test_config.PGEDGE_HOME, "hub", "scripts"))
import ace_config

# Override certificate paths with absolute paths
PKI_BASE = os.path.join(test_config.PGEDGE_HOME, "data", "pg16", "pki")
ace_config.CA_CERT_FILE = os.path.join(PKI_BASE, "ca.crt")
ace_config.ACE_USER_CERT_FILE = os.path.join(
    PKI_BASE, "ace_user-cert", "ace_user.crt"
)
ace_config.ACE_USER_KEY_FILE = os.path.join(
    PKI_BASE, "ace_user-cert", "ace_user.key"
)

# Sets Environment Variables for Commands
os.environ["MY_HOME"] = test_config.PGEDGE_HOME
os.environ["MY_LOGS"] = os.path.join(
    test_config.PGEDGE_HOME, "data", "logs", "cli_log.out"
)
os.environ["MY_LITE"] = os.path.join(
    test_config.PGEDGE_HOME, "data", "conf", "db_local.db"
)
os.environ["MY_CMD"] = "pgedge"


def load_mod(mod: str):
    """Loads a module as a callable object"""
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
    os.chdir(test_config.PGEDGE_HOME)


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
def config():
    return ace_config


@pytest.fixture(scope="class")
def diff_file_path():
    """Fixture to store and share the diff file path between tests"""

    class DiffPathHolder:
        path = None

    return DiffPathHolder


@pytest.fixture(scope="session")
def prepare_databases(config, nodes):
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

            # Creating the tables first
            cur.execute(customers_sql)

            # Loading the data
            with open(test_config.CUSTOMERS_CSV, "r") as f:
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
def cleanup_databases(config, prepare_databases):
    """Cleanup all databases after running tests"""
    # Yield to let the tests run first
    yield

    # Cleanup code that runs after all tests complete
    drop_customers_sql = "DROP TABLE IF EXISTS customers CASCADE;"

    # prepare_databases returns the nodes list
    nodes = prepare_databases

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
            cur = conn.cursor()
            cur.execute(drop_customers_sql)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Failed to cleanup node {node}: {str(e)}")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "abstract_base: mark a test class as an abstract base class "
        "that should not be run directly",
    )


def pytest_collection_modifyitems(items):
    """Skip tests marked as abstract_base if they are in the base class."""
    for item in items:
        if item.get_closest_marker("abstract_base"):
            # Only skip if the test is in TestSimple class directly
            if item.cls and item.cls.__name__ == "TestSimple":
                item.add_marker(pytest.mark.skip(reason="Abstract base class"))
