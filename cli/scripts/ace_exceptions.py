class AceException(Exception):
    pass


class CertificateVerificationError(Exception):
    """Exception raised for errors in certificate verification."""

    pass


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""

    pass