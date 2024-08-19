#  Copyright 2022-2024 PGEDGE  All rights reserved. #


"""ACE is the place of the Anti Chaos Engine"""

import ast
import json
import os
import sys
import re
import subprocess
from datetime import datetime
import logging

import ace_core
import fire
import psycopg
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

import cluster
import util
import ace_db
import ace_config as config
from ace_db import TableDiffTask, TableRepairTask


app = Flask(__name__)

# Configure the root logger
logging.basicConfig()

# Create a StreamHandler for stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

# Get the apscheduler logger and add the handler
apscheduler_logger = logging.getLogger("apscheduler")
apscheduler_logger.setLevel(logging.INFO)
apscheduler_logger.addHandler(stream_handler)


# apscheduler setup
scheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},
    executors={"default": ProcessPoolExecutor(32)},
)


"""
Defining a custom exception class for ACE
"""


class AceException(Exception):
    pass


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def get_dump_file_name(p_prfx, p_schm, p_base_dir="/tmp"):
    return p_base_dir + os.sep + p_prfx + "-" + p_schm + ".sql"


def write_pg_dump(p_ip, p_db, p_port, p_prfx, p_schm, p_base_dir="/tmp"):
    out_file = get_dump_file_name(p_prfx, p_schm, p_base_dir)
    try:
        cmd = f"pg_dump -s -n {p_schm} -h {p_ip} -p {p_port} -d {p_db} > {out_file}"
        os.system(cmd)
    except Exception as e:
        util.exit_exception(e)
    return out_file


"""
Accepts a connection object and returns the version of spock installed

@param: conn - connection object
@return: float - version of spock installed

"""


def get_spock_version(conn):
    data = []
    sql = "SELECT spock.spock_version();"
    try:
        c = conn.cursor()
        c.execute(sql)
        data = c.fetchone()
        if data:
            """
            Spock returns 4.0.0 or something similar.
            We are interested only in the first part of the version
            """
            data = data[0].split(".")[0]
            return float(data)
        else:
            util.exit_message("Could not get spock version from the database")
    except Exception as e:
        util.exit_message("Error in get_spock_version(): " + str(e))

    return 0.0


def fix_schema(diff_file, sql1, sql2):
    newtable = False
    with open(diff_file) as diff_list:
        for i in diff_list.readlines():
            if re.search(r"\\,", i):
                # TODO: Fix this
                # linenum = i.split(",")[0]
                pass
            elif re.search(r"^< CREATE.", i):
                newtable = True
                print(i.replace("<", ""))
            elif re.search(r"^< ALTER.", i):
                print(i.replace("<", ""))
            elif re.search(r"^> CREATE TABLE.", i):
                print(
                    " DROP TABLE " + i.replace("> CREATE TABLE ", "").replace(" (", ";")
                )
            elif newtable:
                print(i.replace("<", ""))
                if re.search(r".;$", i):
                    newtable = False
            else:
                continue
    return 1


def get_row_count(p_con, p_schema, p_table):
    sql = f"SELECT count(*) FROM {p_schema}.{p_table}"

    try:
        cur = p_con.cursor()
        cur.execute(sql)
        r = cur.fetchone()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_row_count():\n" + str(e), 1)

    if not r:
        return 0

    rows = int(r[0])

    return rows


def get_cols(p_con, p_schema, p_table):
    sql = """
    SELECT ordinal_position, column_name
    FROM information_schema.columns
    WHERE table_schema = %s and table_name = %s
    ORDER BY 1, 2
    """

    try:
        cur = p_con.cursor()
        cur.execute(
            sql,
            [
                p_schema,
                p_table,
            ],
        )
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_cols():\n" + str(e), 1)

    if not rows:
        return None

    col_lst = []
    for row in rows:
        col_lst.append(str(row[1]))

    return ",".join(col_lst)


def get_key(p_con, p_schema, p_table):
    sql = """
    SELECT C.COLUMN_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS T,
    INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C
    WHERE c.constraint_name = t.constraint_name
    AND c.table_schema = t.constraint_schema
    AND c.table_schema = %s AND c.table_name = %s
    AND T.CONSTRAINT_TYPE='PRIMARY KEY'
    """

    try:
        cur = p_con.cursor()
        cur.execute(
            sql,
            [
                p_schema,
                p_table,
            ],
        )
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        util.exit_message("Error in get_key():\n" + str(e), 1)

    if not rows:
        return None

    key_lst = []
    for row in rows:
        key_lst.append(str(row[0]))

    return ",".join(key_lst)


def parse_nodes(nodes, quiet_mode=False) -> list:
    node_list = []
    if type(nodes) is str and nodes != "all":
        node_list = [s.strip() for s in nodes.split(",")]
    elif type(nodes) is not str:
        node_list = nodes

    if nodes != "all":
        rep_check = set(node_list)
        if len(rep_check) < len(node_list):
            util.message(
                "Ignoring duplicate node names",
                p_state="warning",
                quiet_mode=quiet_mode,
            )
            node_list = list(rep_check)

    return node_list


def get_row_types(conn, table_name):
    """
    Here we are grabbing the name and data type of each row from table from the
    given conn. Using this complex query instead of a simpler one since this
    gives the correct name of non standard datatypes (i.e. vectors from Vector
    and geometries from PostGIS)
    """

    psql_qry = """
        SELECT
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
        FROM
            pg_catalog.pg_attribute a
        JOIN
            pg_catalog.pg_class c ON a.attrelid = c.oid
        JOIN
            pg_catalog.pg_type t ON a.atttypid = t.oid
        LEFT JOIN
            pg_catalog.pg_namespace n ON c.relnamespace = n.oid
        WHERE
            c.relname = %s
            AND a.attnum > 0
            AND NOT a.attisdropped
        ORDER BY
            a.attnum;
    """

    try:
        cur = conn.cursor()
        cur.execute(psql_qry, (table_name,))
        table_types = {col_name: col_type for col_name, col_type in cur.fetchall()}
    except Exception:
        table_types = dict()

    finally:
        conn.commit()
        if not table_types:
            util.exit_message(
                "Error: couldn't connect to source of truth or find any columns"
            )

    return table_types


def write_diffs_json(diff_dict, row_types, quiet_mode=False):

    def convert_to_json_type(item: str, type: str):
        try:
            if any([s in type for s in ["char", "text", "time"]]):
                return item
            else:
                item = ast.literal_eval(item)
                return item

        except Exception as e:
            util.message(
                f"Could not convert value {item} to {type} while writing to json: {e}",
                p_state="warning",
                quiet_mode=quiet_mode,
            )

        return item

    """
    All diff runs from ACE will be stored in diffs/<date>/diffs_<time>.json
    Each day will have its own directory and each run will have its own file
    that indicates the time of the run.
    """
    now = datetime.now()
    dirname = now.strftime("%Y-%m-%d")
    diff_file_suffix = now.strftime("%H%M%S") + f"{now.microsecond // 1000:03d}"
    diff_filename = "diffs_" + diff_file_suffix + ".json"

    if not os.path.exists("diffs"):
        os.mkdir("diffs")

    dirname = os.path.join("diffs", dirname)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    filename = os.path.join(dirname, diff_filename)

    # Converts diff so that values are correct json type
    write_dict = {
        node_pair: {
            node: [
                {
                    key: convert_to_json_type(val, row_types[key])
                    for key, val in row.items()
                }
                for row in rows
            ]
            for node, rows in nodes_data.items()
        }
        for node_pair, nodes_data in diff_dict.items()
    }

    if not quiet_mode:
        with open(filename, "w") as f:
            f.write(json.dumps(write_dict, default=str))
    else:
        print(json.dumps(write_dict, default=str))

    util.message(
        f"Diffs written out to" f" {util.set_colour(filename, 'blue')}",
        p_state="info",
        quiet_mode=quiet_mode,
    )
    return filename


# TODO: Come up with better naming convention for diff files
def write_diffs_csv(diff_dict):
    import pandas as pd

    """
    All diff runs from ACE will be stored in diffs/<date>/diffs_<time>.json
    Each day will have its own directory and each run will have its own file
    that indicates the time of the run.
    """
    now = datetime.now()
    dirname = now.strftime("%Y-%m-%d")

    if not os.path.exists("diffs"):
        os.mkdir("diffs")

    dirname = os.path.join("diffs", dirname)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    for node_pair in diff_dict.keys():
        diff_file_suffix = now.strftime("%H%M%S") + f"{now.microsecond // 1000:03d}"
        node1, node2 = node_pair.split("/")
        node_str = f"{node1}_{node2}"
        diff_file_name = f"{node_str}_" + diff_file_suffix + ".diff"
        diff_file_path = os.path.join(dirname, diff_file_name)
        t1_file_name = node1 + ".csv"
        t2_file_name = node2 + ".csv"

        t1_write_path = os.path.join(dirname, t1_file_name)
        t2_write_path = os.path.join(dirname, t2_file_name)

        df1 = pd.DataFrame.from_dict(diff_dict[node_pair][node1])
        df2 = pd.DataFrame.from_dict(diff_dict[node_pair][node2])

        df1.to_csv(t1_write_path, header=True, index=False)
        df2.to_csv(t2_write_path, header=True, index=False)

        cmd = f"diff -u {t1_write_path} {t2_write_path} | ydiff > {diff_file_path}"
        subprocess.check_output(cmd, shell=True)

        # Delete the temporary files
        os.remove(t1_write_path)
        os.remove(t2_write_path)

        util.message(
            f"DIFFS BETWEEN {util.set_colour(node1, 'blue')}"
            f" AND {util.set_colour(node2, 'blue')}: {diff_file_path}",
            p_state="info",
        )


def table_diff_checks(td_task: TableDiffTask) -> TableDiffTask:

    if not td_task.cluster_name or not td_task._table_name:
        raise AceException("cluster_name and table_name are required arguments")

    if type(td_task.block_rows) is str:
        try:
            td_task.block_rows = int(td_task.block_rows)
        except Exception:
            raise AceException("Invalid values for ACE_BLOCK_ROWS")
    elif type(td_task.block_rows) is not int:
        raise AceException("Invalid value type for ACE_BLOCK_ROWS")

    # Capping max block size here to prevent the hash function from taking forever
    if td_task.block_rows > config.MAX_ALLOWED_BLOCK_SIZE:
        raise AceException(
            f"Block row size should be <= {config.MAX_ALLOWED_BLOCK_SIZE}"
        )
    if td_task.block_rows < config.MIN_ALLOWED_BLOCK_SIZE:
        raise AceException(
            f"Block row size should be >= {config.MIN_ALLOWED_BLOCK_SIZE}"
        )

    if type(td_task.max_cpu_ratio) is int:
        td_task.max_cpu_ratio = float(td_task.max_cpu_ratio)
    elif type(td_task.max_cpu_ratio) is str:
        try:
            td_task.max_cpu_ratio = float(td_task.max_cpu_ratio)
        except Exception:
            raise AceException("Invalid values for ACE_MAX_CPU_RATIO")
    elif type(td_task.max_cpu_ratio) is not float:
        raise AceException("Invalid value type for ACE_MAX_CPU_RATIO")

    if td_task.max_cpu_ratio > 1.0 or td_task.max_cpu_ratio < 0.0:
        raise AceException(
            "Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio"
        )

    if td_task.output not in ["csv", "json"]:
        raise AceException(
            "table-diff currently supports only csv and json output formats"
        )

    node_list = []
    try:
        node_list = parse_nodes(td_task._nodes)
    except ValueError as e:
        raise AceException(
            f'Nodes should be a comma-separated list of nodenames. \
                E.g., --nodes="n1,n2". Error: {e}'
        )

    if len(node_list) > 3:
        raise AceException(
            "table-diff currently supports up to a three-way table comparison"
        )

    if td_task._nodes != "all" and len(node_list) == 1:
        raise AceException("table-diff needs at least two nodes to compare")

    util.check_cluster_exists(td_task.cluster_name)
    util.message(
        f"Cluster {td_task.cluster_name} exists",
        p_state="success",
        quiet_mode=td_task.quiet_mode,
    )

    nm_lst = td_task._table_name.split(".")
    if len(nm_lst) != 2:
        raise AceException(
            f"TableName {td_task._table_name} must be of form" " 'schema.table_name'"
        )
    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    db, pg, node_info = cluster.load_json(td_task.cluster_name)

    cluster_nodes = []
    database = {}

    if td_task._dbname:
        for db_entry in db:
            if db_entry["db_name"] == td_task._dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        raise AceException(
            f"Database '{td_task._dbname}' not found in cluster"
            " '{td_args.cluster_name}'"
        )

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    if td_task._nodes == "all" and len(cluster_nodes) > 3:
        raise AceException("Table-diff only supports up to three way comparison")

    if td_task._nodes != "all" and len(node_list) > 1:
        for n in node_list:
            if not any(filter(lambda x: x["name"] == n, cluster_nodes)):
                raise AceException("Specified nodenames not present in cluster")

    conn_params = []
    conn_list = []

    try:
        for nd in cluster_nodes:
            if td_task._nodes == "all":
                node_list.append(nd["name"])

            if (node_list and nd["name"] in node_list) or (not node_list):
                params = {
                    "dbname": nd["db_name"],
                    "user": nd["db_user"],
                    "password": nd["db_password"],
                    "host": nd["public_ip"],
                    "port": nd.get("port", 5432),
                }
                conn_list.append(psycopg.connect(**params))
                conn_params.append(params)

    except Exception as e:
        raise AceException("Error in table_diff() Getting Connections:" + str(e), 1)

    util.message(
        "Connections successful to nodes in cluster",
        p_state="success",
        quiet_mode=td_task.quiet_mode,
    )

    cols = None
    key = None

    for conn in conn_list:
        curr_cols = get_cols(conn, l_schema, l_table)
        curr_key = get_key(conn, l_schema, l_table)

        if not curr_cols:
            raise AceException(f"Invalid table name '{td_task._table_name}'")
        if not curr_key:
            raise AceException(f"No primary key found for '{td_task._table_name}'")

        if (not cols) and (not key):
            cols = curr_cols
            key = curr_key
            continue

        if (curr_cols != cols) or (curr_key != key):
            raise AceException("Table schemas don't match")

        cols = curr_cols
        key = curr_key

    util.message(
        f"Table {td_task._table_name} is comparable across nodes",
        p_state="success",
        quiet_mode=td_task.quiet_mode,
    )

    if td_task.diff_file_path:
        
        diff_data = json.load(open(td_task.diff_file_path, "r"))
        try:
            if any(
                [
                    set(list(diff_data[k].keys())) != set(k.split("/"))
                    for k in diff_data.keys()
                ]
            ):
                raise AceException("Contents of diff file improperly formatted")
        except Exception as e:
            raise AceException(f"Contents of diff file improperly formatted: {e}")

    """
    Now that the inputs have been checked and processed, we will populate the
    TableDiffArgs object with the processed values and return it
    """

    """
    We populate the derived fields of TableDiffTask here
    """
    # Psycopg connection objects cannot be pickled easily,
    # so, we send the connection parameters instead
    td_task.fields.conn_params = conn_params
    td_task.fields.cols = cols
    td_task.fields.key = key
    td_task.fields.l_schema = l_schema
    td_task.fields.l_table = l_table
    td_task.fields.node_list = node_list
    td_task.fields.database = database

    return td_task


def table_repair_checks(tr_task: TableRepairTask) -> TableRepairTask:

    # Check if diff_file exists on disk
    if not os.path.exists(tr_task.diff_file_path):
        util.exit_message(f"Diff file {tr_task.diff_file_path} does not exist")

    if type(tr_task.dry_run) is int:
        if tr_task.dry_run < 0 or tr_task.dry_run > 1:
            util.exit_message("Dry run should be True (1) or False (0)")
        tr_task.dry_run = bool(tr_task.dry_run)

    if type(tr_task.dry_run) is not bool:
        util.exit_message("Dry run should be True (1) or False (0)")

    util.check_cluster_exists(tr_task.cluster_name)
    util.message(
        f"Cluster {tr_task.cluster_name} exists",
        p_state="success",
        quiet_mode=tr_task.quiet_mode,
    )

    nm_lst = tr_task._table_name.split(".")
    if len(nm_lst) != 2:
        util.exit_message(
            f"TableName {tr_task._table_name} must be of form" "'schema.table_name'"
        )

    l_schema = nm_lst[0]
    l_table = nm_lst[1]

    db, pg, node_info = cluster.load_json(tr_task.cluster_name)

    cluster_nodes = []
    database = {}

    if tr_task._dbname:
        for db_entry in db:
            if db_entry["db_name"] == tr_task.dbname:
                database = db_entry
                break
    else:
        database = db[0]

    if not database:
        util.exit_message(
            f"Database '{tr_task._dbname}' not found in cluster '"
            f"{tr_task.cluster_name}'"
        )

    # Combine db and cluster_nodes into a single json
    for node in node_info:
        combined_json = {**database, **node}
        cluster_nodes.append(combined_json)

    # Check to see if source_of_truth node is present in cluster
    if not any(node.get("name") == tr_task.source_of_truth for node in cluster_nodes):
        util.exit_message(
            f"Source of truth node {tr_task.source_of_truth} not present in cluster"
        )

    conns = {}
    conn_params = []
    host_map = {}

    try:
        for nd in cluster_nodes:
            params = {
                "dbname": nd["db_name"],
                "user": nd["db_user"],
                "password": nd["db_password"],
                "host": nd["public_ip"],
                "port": nd.get("port", 5432),
            }
            host_map[nd["public_ip"]] = nd["name"]
            conn_params.append(params)
            conns[nd["name"]] = psycopg.connect(**params)

    except Exception as e:
        util.exit_message("Error in diff_tbls() Getting Connections:" + str(e), 1)

    util.message(
        "Connections successful to nodes in cluster",
        p_state="success",
        quiet_mode=tr_task.quiet_mode,
    )

    cols = None
    key = None

    for conn in conns.values():
        curr_cols = get_cols(conn, l_schema, l_table)
        curr_key = get_key(conn, l_schema, l_table)

        if not curr_cols:
            util.exit_message(f"Invalid table name '{tr_task._table_name}'")
        if not curr_key:
            util.exit_message(f"No primary key found for '{tr_task._table_name}'")

        if (not cols) and (not key):
            cols = curr_cols
            key = curr_key
            continue

        if (curr_cols != cols) or (curr_key != key):
            util.exit_message("Table schemas don't match")

        cols = curr_cols
        key = curr_key

    util.message(
        f"Table {tr_task._table_name} is comparable across nodes",
        p_state="success",
        quiet_mode=tr_task.quiet_mode,
    )

    """
    Derived fields for TableRepairTask
    """
    tr_task.fields.cluster_nodes = cluster_nodes
    tr_task.fields.cols = cols
    tr_task.fields.key = key
    tr_task.fields.l_schema = l_schema
    tr_task.fields.l_table = l_table
    tr_task.fields.conn_params = conn_params
    tr_task.fields.host_map = host_map

    return tr_task


def test_function(td_task):
    print("test function", td_task)


@app.route("/ace/table-diff", methods=["GET"])
def table_diff_api():
    from ace_core import table_diff

    cluster_name = request.args.get("cluster_name")
    table_name = request.args.get("table_name")
    dbname = request.args.get("dbname")
    block_rows = request.args.get("block_rows", config.BLOCK_ROWS_DEFAULT)
    max_cpu_ratio = request.args.get("max_cpu_ratio", config.MAX_CPU_RATIO_DEFAULT)
    output = request.args.get("output", "json")
    nodes = request.args.get("nodes", "all")
    batch_size = request.args.get("batch_size", config.BATCH_SIZE_DEFAULT, type=int)
    quiet = request.args.get("quiet", False)

    task_id = ace_db.generate_task_id()

    try:
        raw_args = TableDiffTask(
            cluster_name=cluster_name,
            _table_name=table_name,
            _dbname=dbname,
            block_rows=block_rows,
            max_cpu_ratio=max_cpu_ratio,
            output=output,
            _nodes=nodes,
            batch_size=batch_size,
            quiet_mode=quiet,
        )

        raw_args.scheduler.task_id = task_id
        td_task = table_diff_checks(raw_args)

        ace_db.create_ace_task(task=td_task)
        scheduler.add_job(table_diff, args=(td_task,))

        return jsonify({"task_id": task_id, "submitted_at": datetime.now().isoformat()})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/task-status", methods=["GET"])
def task_status_api():
    task_id = request.args.get("task_id")

    if not task_id:
        return jsonify({"error": "task_id is a required parameter"})

    try:
        task_details = ace_db.get_ace_task_by_id(task_id)
    except Exception as e:
        return jsonify({"error": str(e)})

    if not task_details:
        return jsonify({"error": f"Task {task_id} not found"})

    return jsonify(task_details)


def table_diff_cli(
    cluster_name,
    table_name,
    dbname=None,
    block_rows=config.BLOCK_ROWS_DEFAULT,
    max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
    output="json",
    nodes="all",
    batch_size=config.BATCH_SIZE_DEFAULT,
    quiet=False,
):

    task_id = ace_db.generate_task_id()

    try:
        raw_args = TableDiffTask(
            cluster_name=cluster_name,
            _table_name=table_name,
            _dbname=dbname,
            block_rows=block_rows,
            max_cpu_ratio=max_cpu_ratio,
            output=output,
            _nodes=nodes,
            batch_size=batch_size,
            quiet_mode=quiet,
        )
        raw_args.scheduler.task_id = task_id
        td_task = table_diff_checks(raw_args)
        ace_db.create_ace_task(task=td_task)
        ace_core.table_diff(td_task)
    except AceException as e:
        util.exit_message(str(e))


def table_repair_cli(
    cluster_name,
    diff_file,
    source_of_truth,
    table_name,
    dbname=None,
    dry_run=False,
    quiet=False,
    generate_report=False,
    upsert_only=False,
):

    task_id = ace_db.generate_task_id()

    try:
        raw_args = TableRepairTask(
            cluster_name=cluster_name,
            diff_file_path=diff_file,
            source_of_truth=source_of_truth,
            _table_name=table_name,
            _dbname=dbname,
            dry_run=dry_run,
            quiet_mode=quiet,
            generate_report=generate_report,
            upsert_only=upsert_only,
        )
        raw_args.scheduler.task_id = task_id
        tr_task = table_repair_checks(raw_args)
        ace_db.create_ace_task(task=tr_task)
        ace_core.table_repair(tr_task)
    except AceException as e:
        util.exit_message(str(e))

def table_rerun_cli(
        cluster_name,
        diff_file,
        table_name,
        dbname=None,
        quiet=False,
        behavior="async"
    ):

    task_id = ace_db.generate_task_id()

    if behavior == "async":
        try:
            raw_args = TableDiffTask(
                cluster_name=cluster_name,
                _table_name=table_name,
                _dbname=dbname,
                block_rows=config.BLOCK_ROWS_DEFAULT,
                max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
                output="json",
                _nodes="all",
                batch_size=config.BATCH_SIZE_DEFAULT,
                quiet_mode=quiet,
                diff_file_path=diff_file,
            )
            raw_args.scheduler.task_id = task_id
            td_task = table_diff_checks(raw_args)
            ace_db.create_ace_task(task=td_task)
            ace_core.table_rerun_async(td_task)
        except AceException as e:
            util.exit_message(str(e))

    elif behavior == "temptable":
        try:
            raw_args = TableDiffTask(
                cluster_name=cluster_name,
                _table_name=table_name,
                _dbname=dbname,
                block_rows=config.BLOCK_ROWS_DEFAULT,
                max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
                output="json",
                _nodes="all",
                batch_size=config.BATCH_SIZE_DEFAULT,
                quiet_mode=quiet,
                diff_file_path=diff_file,
            )
            raw_args.scheduler.task_id = task_id
            td_task = table_diff_checks(raw_args)
            ace_db.create_ace_task(task=td_task)
            ace_core.table_rerun_temptable(td_task)
        except AceException as e:
            util.exit_message(str(e))

    else:
        util.exit_message(f"Invalid behavior: {behavior}")


def repset_diff_cli():
    pass


def schema_diff_cli():
    pass


def spock_diff_cli():
    pass


# def listener(event):
#    print("Event:", str(event))


def start_ace():
    ace_db.create_ace_tasks_table()

    # Since the scheduler is a BackgroundScheduler,
    # start() will not block
    scheduler.start()

    # A listener is needed for the upcoming 4.0.0 release
    # of apscheduler. We will need to manually listen to
    # the JOB_ADDED event and then run it. For now, using
    # a BackgroundScheduler with add_job() will automatically
    # run the job in the background.
    # scheduler.add_listener(listener, EVENT_JOB_ADDED)
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    ace_db.create_ace_tasks_table()
    fire.Fire(
        {
            "table-diff": table_diff_cli,
            "table-repair": table_repair_cli,
            "table-rerun": table_rerun_cli,
            "repset-diff": repset_diff_cli,
            "schema-diff": schema_diff_cli,
            "spock-diff": spock_diff_cli,
            "start": start_ace,
        }
    )
