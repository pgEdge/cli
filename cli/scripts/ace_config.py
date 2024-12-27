import os

"""

** ACE CLI and common configuration options **

"""

# ==============================================================================
# Postgres options
STATEMENT_TIMEOUT = 60000  # in milliseconds
CONNECTION_TIMEOUT = 10  # in seconds


#  Default values for ACE table-diff
MAX_DIFF_ROWS = 10000
MIN_ALLOWED_BLOCK_SIZE = 1000
MAX_ALLOWED_BLOCK_SIZE = 100000
BLOCK_ROWS_DEFAULT = os.environ.get("ACE_BLOCK_ROWS", 10000)
MAX_CPU_RATIO_DEFAULT = os.environ.get("ACE_MAX_CPU_RATIO", 0.6)
BATCH_SIZE_DEFAULT = os.environ.get("ACE_BATCH_SIZE", 1)
MAX_BATCH_SIZE = 1000


# Return codes for compare_checksums
BLOCK_OK = 0
MAX_DIFFS_EXCEEDED = 1
BLOCK_MISMATCH = 2
BLOCK_ERROR = 3

# Spock-related options
SPOCK_REPAIR_MODE_MIN_VERSION = 4.0

# ==============================================================================

"""

** ACE Background Service Options **

"""

LISTEN_ADDRESS = "0.0.0.0"
LISTEN_PORT = 5000

"""
Table-diff scheduling options

Specify a list of tables and their crontab schedules or run_frequency as a string.
run_frequency can be string like "1 h", "5 min" or "30 s".
If the crontab_schedule is specified, run_frequency is ignored.
Minimum run_frequency is 5 minutes.

"""
schedule_jobs = [
    {
        "name": "t1",
        "cluster_name": "eqn-t9da",
        "table_name": "public.t1",
    },
    {
        "name": "t2",
        "cluster_name": "eqn-t9da",
        "table_name": "public.t2",
        "args": {
            "max_cpu_ratio": 0.7,
            "batch_size": 1000,
            "block_rows": 10000,
            "nodes": "all",
            "output": "json",
            "quiet": False,
            "dbname": "demo",
        },
    },
    {
        "name": "t3",
        "cluster_name": "eqn-t9da",
        "table_name": "public.t3",
        "args": {
            "max_cpu_ratio": 0.7,
            "batch_size": 1000,
            "block_rows": 10000,
            "nodes": "all",
            "output": "json",
            "quiet": False,
            "dbname": "demo",
        },
    },
]

schedule_config = [
    {
        "job_name": "t1",
        "crontab_schedule": "0 0 * * *",
        "run_frequency": "30s",
        "enabled": False,
        "rerun_after": "1h",
    },
    {
        "job_name": "t2",
        "crontab_schedule": "0 0 * * *",
        "run_frequency": "5s",
        "enabled": False,
        "rerun_after": "1h",
    },
    {
        "job_name": "t3",
        "crontab_schedule": "0 0 * * *",
        "run_frequency": "30s",
        "enabled": False,
        "rerun_after": "1h",
    },
]


# ACE auto-repair options

auto_repair_config = {
    "enabled": True,
    "cluster_name": "eqn-t9da",
    "dbname": "demo",
    "poll_interval": "1000s",
    "status_update_interval": "1000s",
}

# Cert-based auth options

USE_CERT_AUTH = True
ACE_USER_CERT_FILE = "data/pg16/pki/admin-cert/admin.crt"
ACE_USER_KEY_FILE = "data/pg16/pki/admin-cert/admin.key"
CA_CERT_FILE = "data/pg16/pki/ca.crt"

DEBUG_MODE = True

# ==============================================================================
