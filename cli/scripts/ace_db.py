import json
import sqlite3
from typing import Union
import util
import string
import random
from ace_data_models import TableDiffTask, TableRepairTask, RepsetDiffTask

sqlite_db = util.MY_LITE
local_db_conn = sqlite3.connect(sqlite_db, check_same_thread=False)

ace_tasks_sql = """
CREATE TABLE IF NOT EXISTS ace_tasks (
  task_id           TEXT        PRIMARY KEY,
  task_type         TEXT        NOT NULL,
  task_status       TEXT        NOT NULL,
  cluster_name      TEXT        NOT NULL,
  task_context      TEXT,
  schema            TEXT,
  table_name        TEXT,
  repset_name       TEXT,
  diff_file_path    TEXT,
  started_at        TEXT,
  finished_at       TEXT,
  time_taken        DOUBLE
);
"""


def generate_task_id(length=8):
    return "".join(
        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase)
        for _ in range(length)
    )


def create_ace_tasks_table():
    try:
        c = local_db_conn.cursor()
        c.execute(ace_tasks_sql)
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, ace_tasks_sql, "create_ace_tasks_table()")


def create_ace_task(
    task: Union[TableDiffTask, TableRepairTask, RepsetDiffTask]
) -> None:
    try:
        c = local_db_conn.cursor()
        sql = """
                INSERT INTO ace_tasks (task_id, task_type, cluster_name, schema,
                table_name, repset_name, task_status, task_context, diff_file_path,
                started_at, finished_at, time_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              """
        c.execute(
            sql,
            (
                task.scheduler.task_id,
                task.scheduler.task_type,
                task.cluster_name,
                getattr(task.fields, "l_schema", None),
                getattr(task.fields, "l_table", None),
                getattr(task.fields, "repset_name", None),
                task.scheduler.task_status,
                task.scheduler.task_context,
                # diff_file_path is not mandatory for table-diff and repset-diff
                getattr(task, "diff_file_path", None),
                task.scheduler.started_at,
                task.scheduler.finished_at,
                task.scheduler.time_taken,
            ),
        )
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, sql, "create_ace_task()")


def get_ace_task_by_id(task_id) -> dict:
    c = local_db_conn.cursor()
    sql = "SELECT * FROM ace_tasks WHERE task_id = ?"

    # We are using a paramterised query here, so there's no
    # need to explicitly sanitise the input
    c.execute(sql, (task_id,))
    row = c.fetchone()

    if not row:
        return None

    colnames = [desc[0] for desc in c.description]

    task_details = {}

    for colname, value in zip(colnames, row):
        if colname == "task_context":
            task_details[colname] = json.loads(value)
        else:
            task_details[colname] = value

    return task_details


def update_ace_task(task: Union[TableDiffTask, TableRepairTask, RepsetDiffTask]):
    try:
        c = local_db_conn.cursor()
        sql = """
                UPDATE ace_tasks SET
                task_status = ?,
                task_context = ?,
                diff_file_path = ?,
                started_at = ?,
                finished_at = ?,
                time_taken = ?
                WHERE task_id = ?
              """
        c.execute(
            sql,
            (
                task.scheduler.task_status,
                json.dumps(task.scheduler.task_context),
                getattr(task, "diff_file_path", None),
                task.scheduler.started_at.isoformat(timespec="milliseconds"),
                task.scheduler.finished_at.isoformat(timespec="milliseconds"),
                task.scheduler.time_taken,
                task.scheduler.task_id,
            ),
        )
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, sql, "update_ace_task()")


def cleanup_ace_tasks():
    try:
        c = local_db_conn.cursor()
        sql = "DELETE FROM ace_tasks"
        c.execute(sql)
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, sql, "cleanup_ace_tasks()")


def drop_ace_tasks_table():
    try:
        c = local_db_conn.cursor()
        sql = "DROP TABLE IF EXISTS ace_tasks"
        c.execute(sql)
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, sql, "drop_ace_tasks_table()")
