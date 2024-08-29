import ace_config as config
import ace_core
import ace_db
from ace_data_models import (
    RepsetDiffTask,
    SpockDiffTask,
    TableDiffTask,
    TableRepairTask,
)
import ace
import util
from ace_exceptions import AceException


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
        td_task = ace.table_diff_checks(raw_args)
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
        tr_task = ace.table_repair_checks(raw_args)
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
    behavior="multiprocessing",
):

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
        util.exit_message(str(e))

    try:
        if behavior == "multiprocessing":
            ace_core.table_rerun_async(td_task)
        elif behavior == "hostdb":
            ace_core.table_rerun_temptable(td_task)
        else:
            util.exit_message(f"Invalid behavior: {behavior}")
    except AceException as e:
        util.exit_message(str(e))


def repset_diff_cli(
    cluster_name,
    dbname,
    repset_name,
    block_rows=config.BLOCK_ROWS_DEFAULT,
    max_cpu_ratio=config.MAX_CPU_RATIO_DEFAULT,
    output="json",
    nodes="all",
    batch_size=config.BATCH_SIZE_DEFAULT,
    quiet=False,
):

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
            invoke_method="CLI",
        )
        raw_args.scheduler.task_id = task_id
        rd_task = ace.repset_diff_checks(raw_args)
        ace_db.create_ace_task(task=rd_task)
        ace_core.repset_diff(rd_task)
    except AceException as e:
        util.exit_message(str(e))


def spock_diff_cli(
    cluster_name,
    dbname=None,
    nodes="all",
    quiet=False,
):

    task_id = ace_db.generate_task_id()

    try:
        raw_args = SpockDiffTask(
            cluster_name=cluster_name,
            _dbname=dbname,
            _nodes=nodes,
            quiet_mode=quiet,
        )
        raw_args.scheduler.task_id = task_id
        spock_diff_task = ace.spock_diff_checks(raw_args)
        ace_db.create_ace_task(task=spock_diff_task)
        ace_core.spock_diff(spock_diff_task)
    except AceException as e:
        util.exit_message(str(e))


def schema_diff_cli():
    pass
