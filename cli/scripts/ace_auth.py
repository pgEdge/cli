import datetime
import ssl
from functools import wraps
from flask import request, jsonify
import psycopg
import pgpasslib
from cryptography import x509
from cryptography.hazmat.backends import default_backend

import ace_config as config
from ace_exceptions import CertificateVerificationError, AuthenticationError


class ConnectionPool:
    """Manages database connections to avoid creating duplicate connections."""

    def __init__(self):
        self._connections = {}  # {(host, port, db_user, dbname): conn}

    def get_connection(self, host, port, db_user, dbname):
        """
        Get an existing connection or return None if not found.

        Performs thorough connection check to ensure SSL connections are valid.
        """
        key = (host, port, db_user, dbname)
        conn = self._connections.get(key)

        # Check if connection is still alive and valid
        if conn:
            try:
                # First check if connection is closed
                if conn.closed:
                    del self._connections[key]
                    return None

                # Then check if connection is still valid with a transaction
                with conn.cursor() as cur:
                    # Start a transaction to ensure connection is truly alive
                    conn.rollback()  # Clear any previous transaction state
                    cur.execute("BEGIN")
                    cur.execute("SELECT 1")
                    cur.execute("COMMIT")
                return conn
            except Exception:
                # If any error occurs, remove the connection
                if key in self._connections:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    del self._connections[key]
                return None
        return None

    def add_connection(self, host, port, db_user, dbname, conn):
        """Add a new connection to the pool."""
        key = (host, port, db_user, dbname)
        # Close existing connection if it exists
        if key in self._connections:
            try:
                self._connections[key].close()
            except Exception:
                pass
        self._connections[key] = conn

    # TODO: What happens when different scheduling jobs need the same connection?
    def get_cluster_node_connection(
        self, node_info, cluster_name=None, invoke_method="cli", client_role=None
    ):
        """
        Create a database connection to a cluster node with proper authentication.

        Args:
            node_info: Dictionary containing node connection information:
                - db_name: Database name
                - db_user: Database user
                - public_ip: Host IP/name
                - port: Port number
                - db_password: Password (optional)
                - name: Node name
            cluster_name: Name of the cluster (for error messages)
            invoke_method: Either "cli" or "api" to determine auth method
            client_role: Role to switch to after connection (used in API mode)

        Returns:
            tuple: (connection_params, connection)

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            host = node_info["public_ip"]
            port = node_info.get("port", 5432)
            db_user = node_info["db_user"]
            dbname = node_info["db_name"]

            params = {
                "dbname": dbname,
                "user": db_user,
                "host": host,
                "port": port,
                "options": f"-c statement_timeout={config.STATEMENT_TIMEOUT}",
                "application_name": "ACE",
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                "connect_timeout": config.CONNECTION_TIMEOUT,
            }

            # Check connection pool first
            conn = self.get_connection(host, port, db_user, dbname)
            if conn:
                # If we're in API mode we have to switch to the user's role
                # for security reasons. However, if ACE is being invoked through
                # the CLI, we don't have to worry about this.
                if config.USE_CERT_AUTH and client_role:
                    with conn.cursor() as cur:
                        cur.execute(f"SET ROLE {client_role}")
                return params, conn

            if config.USE_CERT_AUTH:
                if config.ACE_USER_CERT_FILE and config.ACE_USER_KEY_FILE:
                    params.update(
                        {
                            "sslmode": "verify-full",
                            "sslcert": config.ACE_USER_CERT_FILE,
                            "sslkey": config.ACE_USER_KEY_FILE,
                            "sslrootcert": config.CA_CERT_FILE,
                        }
                    )
                else:
                    raise AuthenticationError(
                        "Client certificate authentication is enabled but no"
                        "certificate files are provided"
                    )
            else:
                if invoke_method == "api":
                    raise AuthenticationError(
                        "Client certificate authentication needs to be enabled"
                        "for API usage"
                    )
                # Handle password authentication
                if node_info["db_password"]:
                    params["password"] = node_info["db_password"]
                else:
                    pgpass = pgpasslib.getpass(
                        host=node_info["name"],
                        user=db_user,
                        dbname=dbname,
                        port=port,
                    )
                    if not pgpass:
                        msg = f"No password found for {node_info['name']}"
                        if cluster_name:
                            msg += f" in {cluster_name}.json or ~/.pgpass"
                        raise AuthenticationError(msg)
                    params["password"] = pgpass

            conn = psycopg.connect(**params)

            # Here again, we need to switch to the user's role if we're in API mode
            if config.USE_CERT_AUTH and client_role:
                with conn.cursor() as cur:
                    cur.execute(f"SET ROLE {client_role}")

            self.add_connection(host, port, db_user, dbname, conn)
            return params, conn

        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(
                f"Failed to connect to node {node_info['public_ip']}: {str(e)}"
            )

    def close_all(self):
        """Close all connections in the pool."""
        for conn in self._connections.values():
            try:
                conn.close()
            except Exception:
                pass
        self._connections.clear()


def extract_common_name(cert_data):
    """
    Extract the Common Name from a certificate.

    Args:
        cert_data: The certificate data in PEM or DER format

    Returns:
        str: The Common Name from the certificate

    Raises:
        CertificateVerificationError: If CN cannot be extracted
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        for attr in cert.subject:
            if attr.oid == x509.NameOID.COMMON_NAME:
                return attr.value
        raise CertificateVerificationError("No Common Name found in certificate")
    except Exception as e:
        msg = f"Failed to extract CN from certificate: {str(e)}"
        raise CertificateVerificationError(msg)


def verify_client_cert(cert_data, ca_cert_path=None):
    """
    Verify a client certificate against the CA certificate.

    Args:
        cert_data: The client certificate data
        ca_cert_path: Path to the CA certificate file. If None, uses
            config.CA_CERT_FILE

    Returns:
        bool: True if verification succeeds

    Raises:
        CertificateVerificationError: If verification fails
    """
    try:
        if ca_cert_path is None:
            ca_cert_path = config.CA_CERT_FILE

        context = ssl.create_default_context(cafile=ca_cert_path)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        # Verify certificate is properly formatted and not expired
        if not cert:
            raise CertificateVerificationError("Invalid certificate format")

        if cert.not_valid_after_utc <= cert.not_valid_before_utc:
            raise CertificateVerificationError(
                "Certificate has invalid validity period"
            )

        # Use timezone-aware datetime for comparison
        current_time = datetime.datetime.now(datetime.timezone.utc)
        if (
            current_time < cert.not_valid_before_utc
            or current_time > cert.not_valid_after_utc
        ):
            raise CertificateVerificationError("Certificate is not currently valid")

        return True
    except CertificateVerificationError:
        raise
    except Exception as e:
        raise CertificateVerificationError(f"Certificate verification failed: {str(e)}")


def require_client_cert(f):
    """
    Decorator to require and verify client certificates for API endpoints.

    Usage:
        @app.route('/some-endpoint')
        @require_client_cert
        def protected_endpoint():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get client certificate from request environment
            if "SSL_CLIENT_CERT" not in request.environ:
                return jsonify({"error": "Client certificate required"}), 401

            cert_data = request.environ["SSL_CLIENT_CERT"].encode("utf-8")

            # Verify certificate using CA cert from config
            verify_client_cert(cert_data)

            # Extract CN
            client_cn = extract_common_name(cert_data)

            # Add CN to request context for use in the endpoint
            request.client_cn = client_cn

            return f(*args, **kwargs)
        except CertificateVerificationError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

    return decorated_function
