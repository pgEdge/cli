import sqlite3
import util
import string
import random

sqlite_db = util.MY_LITE
local_db_conn = sqlite3.connect(sqlite_db)

ace_tasks_sql = """
CREATE TABLE IF NOT EXISTS ace_tasks (
  task_id            TEXT        PRIMARY KEY,
  task_type          TEXT        NOT NULL,
  cluster_name      TEXT        NOT NULL,
  schema            TEXT        NOT NULL,
  table_name        TEXT        NOT NULL,
  task_status        TEXT        NOT NULL,
  task_context       TEXT        NOT NULL
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
    task_id, task_type, cluster_name, schema, table_name, task_status, task_context
):
    try:
        c = local_db_conn.cursor()
        sql = """
                INSERT INTO ace_tasks (task_id, task_type, cluster_name, schema,
                table_name, task_status, task_context) VALUES (?, ?, ?, ?, ?, ?, ?)
              """
        c.execute(
            sql,
            (
                task_id,
                task_type,
                cluster_name,
                schema,
                table_name,
                task_status,
                task_context,
            ),
        )
        local_db_conn.commit()
    except Exception as e:
        util.fatal_sql_error(e, sql, "create_ace_task()")


def get_ace_task_by_id(task_id):
    try:
        c = local_db_conn.cursor()
        sql = "SELECT * FROM ace_tasks WHERE task_id = ?"
        c.execute(sql, (task_id,))
        return c.fetchone()
    except Exception as e:
        util.fatal_sql_error(e, sql, "get_ace_task_by_id()")


def update_ace_task(task_id, task_status, task_context):
    try:
        c = local_db_conn.cursor()
        sql = """
                UPDATE ace_tasks SET task_status = ?, task_context = ?
                WHERE task_id = ?
              """
        c.execute(sql, (task_status, task_context, task_id))
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
