import pytest

from test_simple_base import TestSimpleBase


class TestCertAuth(TestSimpleBase):

    @pytest.fixture(scope="class", autouse=True)
    def setup_cert_auth(self, config):
        config.USE_CERT_AUTH = True

    def test_cert_auth_setup(self, config):
        assert config.USE_CERT_AUTH is True
        assert config.CA_CERT_FILE is not None
        assert config.ACE_USER_CERT_FILE is not None
        assert config.ACE_USER_KEY_FILE is not None

        try:
            with open(config.CA_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read CA certificate file: {str(e)}")

        try:
            with open(config.ACE_USER_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user certificate file: {str(e)}")

        try:
            with open(config.ACE_USER_KEY_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user key file: {str(e)}")

    @pytest.mark.parametrize("use_cert_auth", [True])
    def test_database_connectivity(self, nodes, use_cert_auth):
        super().test_database_connectivity(nodes, use_cert_auth)

    def test_simple_table_diff(self, cli, capsys, table_name):
        super().test_simple_table_diff(cli, capsys, table_name)

    def test_table_diff_with_differences(
        self, cli, capsys, table_name, diff_file_path, use_cert_auth
    ):
        super().test_table_diff_with_differences(
            cli, capsys, table_name, diff_file_path, use_cert_auth
        )

    def test_simple_table_repair(self, cli, capsys, table_name, diff_file_path):
        super().test_simple_table_repair(cli, capsys, table_name, diff_file_path)

    @pytest.mark.parametrize("use_cert_auth", [True])
    def test_table_rerun_temptable(
        self, cli, capsys, table_name, diff_file_path, use_cert_auth
    ):
        super().test_table_rerun_temptable(
            cli, capsys, table_name, diff_file_path, use_cert_auth
        )

    def test_table_rerun_multiprocessing(self, cli, capsys, table_name, diff_file_path):
        super().test_table_rerun_multiprocessing(
            cli, capsys, table_name, diff_file_path
        )
