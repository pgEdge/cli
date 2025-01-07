import pytest
import psycopg
from test_simple import TestSimple


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
        self, cli, capsys, table_name, column_name, key_column, diff_file_path
    ):
        return super().test_table_diff_with_differences(
            cli, capsys, table_name, column_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        return super().test_simple_table_repair(
            cli, capsys, table_name, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(
        self, cli, capsys, table_name, key_column, diff_file_path
    ):
        return super().test_table_rerun_temptable(
            cli, capsys, table_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.CuStOmErS"])
    def test_table_rerun_multiprocessing(
        self, cli, capsys, table_name, diff_file_path
    ):
        return super().test_table_rerun_multiprocessing(
            cli, capsys, table_name, diff_file_path
        )
