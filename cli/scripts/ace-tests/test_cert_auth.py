import pytest

from test_simple_base import TestSimpleBase


class TestCertAuth(TestSimpleBase):

    @pytest.fixture(scope="class", autouse=True)
    def setup_cert_auth(self, ace_conf):
        ace_conf.USE_CERT_AUTH = True

    @pytest.mark.order(1)
    def test_cert_auth_setup(self, ace_conf):
        assert ace_conf.USE_CERT_AUTH is True
        assert ace_conf.CA_CERT_FILE is not None
        assert ace_conf.ACE_USER_CERT_FILE is not None
        assert ace_conf.ACE_USER_KEY_FILE is not None

        try:
            with open(ace_conf.CA_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read CA certificate file: {str(e)}")

        try:
            with open(ace_conf.ACE_USER_CERT_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user certificate file: {str(e)}")

        try:
            with open(ace_conf.ACE_USER_KEY_FILE, "r") as f:
                assert f.read() is not None
        except Exception as e:
            pytest.fail(f"Failed to read ACE user key file: {str(e)}")

    pass
