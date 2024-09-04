from datetime import datetime
import pickle
import _pickle as cPickle

from flask import Flask, jsonify, request
from apscheduler.events import EVENT_JOB_ERROR

import ace
import ace_config as config
import ace_core
import ace_db
from ace_data_models import (
    RepsetDiffTask,
    SchemaDiffTask,
    SpockDiffTask,
    TableDiffTask,
    TableRepairTask,
)
from ace_exceptions import AceException


app = Flask(__name__)


@app.route("/ace/table-diff", methods=["GET"])
def table_diff_api():
    cluster_name = request.args.get("cluster_name")
    table_name = request.args.get("table_name")
    dbname = request.args.get("dbname", None)
    block_rows = request.args.get("block_rows", config.BLOCK_ROWS_DEFAULT)
    max_cpu_ratio = request.args.get("max_cpu_ratio", config.MAX_CPU_RATIO_DEFAULT)
    output = request.args.get("output", "json")
    nodes = request.args.get("nodes", "all")
    batch_size = request.args.get("batch_size", config.BATCH_SIZE_DEFAULT, type=int)
    quiet = request.args.get("quiet", False)

    if not cluster_name or not table_name:
        return jsonify({"error": "cluster_name and table_name are required parameters"})

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
            skip_db_update=False,
        )

        raw_args.scheduler.task_id = task_id
        td_task = ace.table_diff_checks(raw_args)

        ace_db.create_ace_task(task=td_task)
        td_job = ace.scheduler.add_job(
            ace_core.table_diff,
            args=(td_task,),
        )

        #pickled_task = pickle.dumps(td_task, protocol=pickle.HIGHEST_PROTOCOL)
        #ace_db.store_pickled_task(td_job.id, pickled_task)

        return jsonify({"task_id": task_id, "submitted_at": datetime.now().isoformat()})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/table-repair", methods=["GET"])
def table_repair_api():
    cluster_name = request.args.get("cluster_name")
    diff_file = request.args.get("diff_file")
    source_of_truth = request.args.get("source_of_truth")
    table_name = request.args.get("table_name")
    dbname = request.args.get("dbname")
    dry_run = request.args.get("dry_run", False)
    quiet = request.args.get("quiet", False)
    generate_report = request.args.get("generate_report", False)
    upsert_only = request.args.get("upsert_only", False)

    if not cluster_name or not diff_file or not source_of_truth or not table_name:
        return jsonify(
            {
                "error": "cluster_name, diff_file, source_of_truth, and table_name"
                "are required parameters"
            }
        )

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
        tr_task = ace.table_repair_checks(raw_args)
        ace_db.create_ace_task(task=tr_task)

        ace.scheduler.add_job(ace_core.table_repair, args=(tr_task,))
        return jsonify({"task_id": task_id, "submitted_at": datetime.now().isoformat()})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/table-rerun", methods=["GET"])
def table_rerun_api():
    cluster_name = request.args.get("cluster_name")
    diff_file = request.args.get("diff_file")
    table_name = request.args.get("table_name")
    dbname = request.args.get("dbname", None)
    quiet = request.args.get("quiet", False)
    behavior = request.args.get("behavior", "multiprocessing")

    if not cluster_name or not diff_file or not table_name:
        return jsonify(
            {
                "error": "cluster_name, diff_file, and table_name"
                "are required parameters"
            }
        )

    task_id = ace_db.generate_task_id()

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
        td_task = ace.table_diff_checks(raw_args)
        ace_db.create_ace_task(task=td_task)
    except AceException as e:
        return jsonify({"error": str(e)})

    try:
        if behavior == "multiprocessing":
            ace.scheduler.add_job(ace_core.table_rerun_async, args=(td_task,))
            return jsonify(
                {"task_id": task_id, "submitted_at": datetime.now().isoformat()}
            )
        elif behavior == "hostdb":
            ace.scheduler.add_job(ace_core.table_rerun_temptable, args=(td_task,))
            return jsonify(
                {"task_id": task_id, "submitted_at": datetime.now().isoformat()}
            )
        else:
            return jsonify({"error": f"Invalid behavior: {behavior}"})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/repset-diff", methods=["GET"])
def repset_diff_api():
    cluster_name = request.args.get("cluster_name")
    repset_name = request.args.get("repset_name")
    dbname = request.args.get("dbname", None)
    block_rows = request.args.get("block_rows", config.BLOCK_ROWS_DEFAULT)
    max_cpu_ratio = request.args.get("max_cpu_ratio", config.MAX_CPU_RATIO_DEFAULT)
    output = request.args.get("output", "json")
    nodes = request.args.get("nodes", "all")
    batch_size = request.args.get("batch_size", config.BATCH_SIZE_DEFAULT, type=int)
    quiet = request.args.get("quiet", False)

    if not cluster_name or not repset_name:
        return jsonify(
            {"error": "cluster_name and repset_name are required parameters"}
        )

    task_id = ace_db.generate_task_id()

    try:
        raw_args = RepsetDiffTask(
            cluster_name=cluster_name,
            _dbname=dbname,
            repset_name=repset_name,
            block_rows=block_rows,
            max_cpu_ratio=max_cpu_ratio,
            output=output,
            _nodes=nodes,
            batch_size=batch_size,
            quiet_mode=quiet,
            invoke_method="API",
        )

        raw_args.scheduler.task_id = task_id
        rd_task = ace.repset_diff_checks(raw_args)
        ace_db.create_ace_task(task=rd_task)
        ace.scheduler.add_job(ace_core.repset_diff, args=(rd_task,))
        return jsonify({"task_id": task_id, "submitted_at": datetime.now().isoformat()})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/spock-diff", methods=["GET"])
def spock_diff_api():
    cluster_name = request.args.get("cluster_name")
    dbname = request.args.get("dbname", None)
    nodes = request.args.get("nodes", "all")
    quiet = request.args.get("quiet", False)

    if not cluster_name:
        return jsonify({"error": "cluster_name is a required parameter"})

    task_id = ace_db.generate_task_id()

    try:
        raw_args = SpockDiffTask(
            cluster_name=cluster_name,
            _dbname=dbname,
            _nodes=nodes,
            quiet_mode=quiet,
        )

        raw_args.scheduler.task_id = task_id
        sd_task = ace.spock_diff_checks(raw_args)
        ace_db.create_ace_task(task=sd_task)
        ace.scheduler.add_job(ace_core.spock_diff, args=(sd_task,))
        return jsonify({"task_id": task_id, "submitted_at": datetime.now().isoformat()})
    except AceException as e:
        return jsonify({"error": str(e)})


@app.route("/ace/schema-diff", methods=["GET"])
def schema_diff_api():
    cluster_name = request.args.get("cluster_name")
    schema_name = request.args.get("schema_name")
    dbname = request.args.get("dbname", None)
    nodes = request.args.get("nodes", "all")
    quiet = request.args.get("quiet", False)

    task_id = ace_db.generate_task_id()

    if not cluster_name or not schema_name:
        return jsonify(
            {"error": "cluster_name and schema_name are required parameters"}
        )

    try:
        raw_args = SchemaDiffTask(
            cluster_name=cluster_name,
            schema_name=schema_name,
            _dbname=dbname,
            _nodes=nodes,
            quiet_mode=quiet,
        )

        raw_args.scheduler.task_id = task_id
        sd_task = ace.schema_diff_checks(raw_args)
        ace_db.create_ace_task(task=sd_task)
        ace.scheduler.add_job(ace_core.schema_diff, args=(sd_task,))
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


def start_ace():
    ace_db.drop_ace_tables()
    ace_db.create_ace_tables()

    # Since the scheduler is a BackgroundScheduler,
    # start() will not block
    ace.scheduler.start()
    # ace.scheduler.add_listener(ace.error_listener, EVENT_JOB_ERROR)

    # A listener is needed for the upcoming 4.0.0 release
    # of apscheduler. We will need to manually listen to
    # the JOB_ADDED event and then run it. For now, using
    # a BackgroundScheduler with add_job() will automatically
    # run the job in the background.
    # scheduler.add_listener(listener, EVENT_JOB_ADDED)
    app.run(host="127.0.0.1", port=5000, debug=True)
