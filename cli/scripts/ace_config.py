import os

# Postgres options
STATEMENT_TIMEOUT = 60000


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


"""
Table-diff scheduling options

Specify a list of tables and their crontab schedules or run_frequency as a string.
run_frequency can be string like "1 h", "5 min" or "30 s".
If the crontab_schedule is specified, run_frequency is ignored.

"""
schedule_config = [
    {
        "cluster_name": "eqn-t9da",
        "table_name": "public.t1",
        # "crontab_schedule": "0 0 * * *",
        "run_frequency": "30s",
        "enabled": True,
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
        "cluster_name": "eqn-t9da",
        "table_name": "public.t2",
        # "crontab_schedule": "0 0 * * *",
        "run_frequency": "45s",
        "enabled": True,
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
        "cluster_name": "eqn-t9da",
        "table_name": "public.t3",
        # "crontab_schedule": "0 0 * * *",
        "run_frequency": "1min",
        "enabled": True,
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
