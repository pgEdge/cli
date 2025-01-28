import pytest
import psycopg
import abc


@pytest.mark.usefixtures("prepare_databases")
@pytest.mark.abstract_base
class TestSimpleBase(abc.ABC):
    """Abstract base class for ACE operation tests.
    This class should not be run directly, but instead should be inherited
    by concrete test classes."""

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def _introduce_differences(
        self,
        ace_conf,
        node,
        table_name,
        column_name,
        key_column,
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
            "application_name": "ace-tests",
        }
        if ace_conf.USE_CERT_AUTH:
            params["sslmode"] = "verify-full"
            params["sslrootcert"] = ace_conf.CA_CERT_FILE
            params["sslcert"] = ace_conf.ADMIN_CERT_FILE
            params["sslkey"] = ace_conf.ADMIN_KEY_FILE

        conn = psycopg.connect(**params)

        # TODO: Find a way to assert that the connection is using SSL
        if ace_conf.USE_CERT_AUTH:
            pass

        cur = conn.cursor()
        cur.execute("SELECT spock.repair_mode(true)")

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

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    def test_database_connectivity(self, ace_conf, nodes):
        """Test that we can connect to all prepared databases"""
        pass

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        """Test table diff on cluster eqn-t9da for specified table"""
        pass

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_differences(
        self,
        cli,
        capsys,
        ace_conf,
        table_name,
        column_name,
        key_column,
        diff_file_path,
    ):
        """Test table diff when differences exist between nodes"""
        pass

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        """Test table repair on cluster eqn-t9da for specified table"""
        pass

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(
        self, cli, capsys, ace_conf, table_name, key_column, diff_file_path
    ):
        """Test table rerun temptable on cluster eqn-t9da for specified table"""
        pass

    @abc.abstractmethod
    @pytest.mark.skip(reason="Abstract base class method")
    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name, diff_file_path):
        """Test table rerun multiprocessing on cluster eqn-t9da"""
        pass
