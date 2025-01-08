import pytest

from test_simple import TestSimple


@pytest.mark.usefixtures("prepare_databases", "setup_cert_auth")
class TestCertAuth(TestSimple):

    @pytest.fixture(scope="class", autouse=True)
    def setup_cert_auth(self, ace_conf):
        ace_conf.USE_CERT_AUTH = True

    def test_cert_auth_setup(self, ace_conf):
        assert ace_conf.USE_CERT_AUTH is True
        assert ace_conf.CA_CERT_FILE is not None
        assert ace_conf.ADMIN_CERT_FILE is not None
        assert ace_conf.ADMIN_KEY_FILE is not None

        try:
            with open(ace_conf.CA_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read CA certificate file: {str(e)}")

        try:
            with open(ace_conf.ADMIN_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user certificate file: {str(e)}")

        try:
            with open(ace_conf.ADMIN_KEY_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user key file: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_diff(self, cli, capsys, table_name):
        return super().test_simple_table_diff(cli, capsys, table_name)

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_differences(
        self, cli, capsys, ace_conf, table_name, column_name, key_column, diff_file_path
    ):
        return super().test_table_diff_with_differences(
            cli, capsys, ace_conf, table_name, column_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        return super().test_simple_table_repair(cli, capsys, table_name, diff_file_path)

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(
        self, cli, capsys, ace_conf, table_name, key_column, diff_file_path
    ):
        return super().test_table_rerun_temptable(
            cli, capsys, ace_conf, table_name, key_column, diff_file_path
        )

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_table_rerun_multiprocessing(self, cli, capsys, table_name, diff_file_path):
        return super().test_table_rerun_multiprocessing(
            cli, capsys, table_name, diff_file_path
        )
