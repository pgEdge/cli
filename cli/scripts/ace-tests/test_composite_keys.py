import pytest
import psycopg
from test_simple import TestSimple


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
        self, cli, capsys, table_name, column_name, key_column, diff_file_path
    ):
        return super().test_table_diff_with_differences(
            cli, capsys, table_name, column_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        return super().test_simple_table_repair(
            cli, capsys, table_name, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["InDeX"])
    def test_table_rerun_temptable(
        self, cli, capsys, table_name, key_column, diff_file_path
    ):
        return super().test_table_rerun_temptable(
            cli, capsys, table_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(
        self, cli, capsys, table_name, diff_file_path
    ):
        return super().test_table_rerun_multiprocessing(
            cli, capsys, table_name, diff_file_path
        )
