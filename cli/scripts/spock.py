
#  Copyright 2022-2024 PGEDGE  All rights reserved. #


import sys, os, subprocess, time
import util, fire, psycopg

nc = "./ctl "

isAutoStart = str(os.getenv("isAutoStart", "False"))

#  force use of PGPASSWORD from ~/.pgpass
os.environ["PGPASSWORD"] = ""


def error_exit(p_msg, p_rc=1):
    util.message("ERROR: " + p_msg)
    if util.debug_lvl() == 0:
        os.system(nc + "remove pgedge")

    sys.exit(p_rc)


def change_pg_pwd(pwd_file, db="*", user="postgres", host="localhost", pg=None):
    pg_v = util.get_pg_v(pg)
    dbp = util.get_column("port", pg_v)

    if os.path.isfile(pwd_file):
        file = open(pwd_file, "r")
        line = file.readline()
        pg_password = line.rstrip()
        file.close()
        os.system("rm " + pwd_file)
    else:
        util.exit_message("invalid pwd file: " + str(pwd_file), 1)

    rc = util.change_pgpassword(
        p_passwd=pg_password, p_port=dbp, p_host=host, p_db="*", p_user=user, p_ver=pg_v
    )
    sys.exit(rc)


def get_eq(parm, val, sufx, set=False):
    if set:
        colon_equal = str(parm) + " := '{" + str(val) + "}'" + str(sufx)
    else:
        colon_equal = str(parm) + " := '" + str(val) + "'" + str(sufx)
    return colon_equal


def node_add_interface(node_name, interface_name, dsn, db, pg=None):
    """Add a new node interface.
    
        Add an additional interface to a spock node. \n
        Example: spock node-add-interface n1 n1_2 'host=10.1.2.5 user=pgedge dbname=demo' demo
        :param node_name: The name of the node. 
        Should reference the node already created in this database. 
        Example: n1
        :param interface_name: The interface name to add to the node.
        The interface created by default matches the node name, add a new interface with a unique name.
        Example: n1_2
        :param dsn: The additional connection string to the node.
        The user in this string should equal the OS user. 
        This connection string should be reachable from outside and match the one used later in the sub-create command. 
        Example: 'host=10.1.2.5 port= 5432 user=pgedge dbname=demo'
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.node_add_interface("
        + get_eq("node_name", node_name, ", ")
        + get_eq("interface_name", interface_name, ", ")
        + get_eq("dsn", dsn, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def node_drop_interface(node_name, interface_name, db, pg=None):
    """Delete a node interface.

        Drop an interface from a spock node. \n
        Example: spock node-drop-interface n1 n1_2 demo
        :param node_name: The name of the node.  
        Example: n1
        :param interface_name: The interface name to remove from the node.
        Example: n1_2
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.node_drop_interface("
        + get_eq("node_name", node_name, ", ")
        + get_eq("interface_name", interface_name, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def node_create(node_name, dsn, db, pg=None):
    """Define a node for spock.

        Create a spock node. \n
        Example: spock node-create n1 'host=10.1.2.5 user=pgedge dbname=demo' demo
        :param node_name: The name of the node. 
        Only one node is allowed per database, and each node in a cluster must have a unique name. 
        To use snowflake, use the convention n1,n2, etc.
        Example: n1
        :param dsn: The connection string to the node.
        The user in this string should equal the OS user. 
        This connection string should be reachable from outside and match the one used later in the sub-create command. 
        Example: 'host=10.1.2.5 port= 5432 user=pgedge dbname=demo'
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.node_create("
        + get_eq("node_name", node_name, ", ")
        + get_eq("dsn", dsn, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    if node_name[0] == "n" and node_name[1].isdigit():
        cmd = f"db guc-set snowflake.node {node_name[1]}"
        os.system(nc + cmd)
    sys.exit(0)


def node_drop(node_name, db, pg=None):
    """Remove a spock node.

        Drop a spock node. \n
        Example: spock node-drop n1 demo
        :param node_name: The name of the node.
        Example: n1
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.node_drop(" + get_eq("node_name", node_name, ")")
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def node_alter_location(node_name, location, db, pg=None):
    """Set location details for spock node."""

    pg_v = util.get_pg_v(pg)

    [location_nm, country, state, lattitude, longitude] = util.get_location_dtls(
        location
    )

    sql = """
UPDATE spock.node
   SET location_nm = ?, country = ?, state = ?, lattitude = ?, longitude = ?
 WHERE location = ?
"""

    con = util.get_pg_connection(pg_v, db, util.get_user())

    rc = 0
    try:
        con = util.get_pg_connection(pg_v, "postgres", util.get_user())
        cur = con.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute(sql, [location_nm, country, state, lattitude, longitude])
        con.commit()
    except Exception as e:
        util.print_exception(e)
        con.rollback()
        rc = 1

    sys.exit(rc)


def node_list(db, pg=None):
    """Display node table. 
        
        List all nodes registered in a database. If replication is configured correctly, this will list all nodes in the cluster. \n
        Example: spock node-list demo
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = """
SELECT node_id, node_name FROM spock.node ORDER BY node_name
"""
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_create(
    set_name,
    db,
    replicate_insert=True,
    replicate_update=True,
    replicate_delete=True,
    replicate_truncate=True,
    pg=None,
):
    """Define a replication set.

        Create a replication set. \n
        Example: spock repset-create demo_repset demo
        :param set_name: The name of the replication set. 
        Example: demo_repset
        :param db: The name of the database. 
        Example: demo
        :param replicate_insert: For tables in this replication set, replicate inserts. 
        :param replicate_update: For tables in this replication set, replicate updates.
        :param replicate_delete: For tables in this replication set, replicate deletes.
        :param replicate_truncate: For tables in this replication set, replicate truncate.
        
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.repset_create("
        + get_eq("set_name", set_name, ", ")
        + get_eq("replicate_insert", replicate_insert, ", ")
        + get_eq("replicate_update", replicate_update, ", ")
        + get_eq("replicate_delete", replicate_delete, ", ")
        + get_eq("replicate_truncate", replicate_truncate, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_alter(
    set_name,
    db,
    replicate_insert=True,
    replicate_update=True,
    replicate_delete=True,
    replicate_truncate=True,
    pg=None,
):
    """Modify a replication set.

        Alter a replication set. \n
        Example: spock repset-alter demo_repset demo --replicate_truncate=False
        :param set_name: The name of the replication set. 
        Example: demo_repset
        :param db: The name of the database. 
        Example: demo
        :param replicate_insert: For tables in this replication set, replicate inserts. 
        :param replicate_update: For tables in this replication set, replicate updates.
        :param replicate_delete: For tables in this replication set, replicate deletes.
        :param replicate_truncate: For tables in this replication set, replicate truncate.
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.repset_alter("
        + get_eq("set_name", set_name, ", ")
        + get_eq("replicate_insert", replicate_insert, ", ")
        + get_eq("replicate_update", replicate_update, ", ")
        + get_eq("replicate_delete", replicate_delete, ", ")
        + get_eq("replicate_truncate", replicate_truncate, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_drop(set_name, db, pg=None):
    """Remove a replication set.

        Drop a replication set. \n
        Example: spock repset-drop demo_repset demo
        :param set_name: The name of the replication set. 
        Example: demo_repset
        :param db: The name of the database. 
        Example: demo

    """
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.repset_drop(" + get_eq("set_name", set_name, ")")
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_add_seq(replication_set, sequence, db, synchronize_data=False, pg=None):
    """Add a sequence to a replication set."""
    pg_v = util.get_pg_v(pg)
    seqs = util.get_seq_list(sequence, db, pg_v)

    for sequence in seqs:
        seq = str(sequence[0])
        sql = (
            "SELECT spock.repset_add_seq("
            + get_eq("set_name", replication_set, ", ")
            + get_eq("relation", seq, ", ")
            + get_eq("synchronize_data", synchronize_data, ")")
        )
        util.run_psyco_sql(pg_v, db, sql)
        util.message(f"Adding sequence {seq} to replication set {replication_set}.")
    sys.exit(0)


def repset_remove_seq(set_name, relation, db, pg=None):
    """Remove a sequence from a replication set."""
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.repset_remove_seq("
        + get_eq("set_name", set_name, ", ")
        + get_eq("relation", relation, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_add_partition(parent_table, db, partition=None, row_filter=None, pg=None):
    """Add a partition to a replication set.

        Add a partition to the same replication set that the parent table is a part of. \n
        Example: spock repset-add-partition mytable demo --partition=mytable_202012
        :param parent_table: The name of the parent table.
        Example: mytable
        :param db: The name of the database. 
        Example: demo
        :param partition: The name of the partition. If none is provided, it will add all unreplicated partitions to the replication set.
        Example: mytable_202012
        :param row_filter: The row filtering expression. 
        Example: 'my_id = 1001'
    """
    util.exit_message("Not implemented yet.")
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.repset_add_partition(" + get_eq("parent", parent_table, "")
    if partition:
        sql = sql + "," + get_eq("partition", partition, "")
    if row_filter:
        sql = sql + "," + get_eq("row_filter", row_filter, "")
    sql = sql + ")"
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_remove_partition(parent_table, db, partition=None, pg=None):
    """Remove a partition from a replication set.

        Remove a partition from the replication set that the parent table is a part of. \n
        Example: spock repset-remove-partition mytable demo --partition=mytable_202012
        :param parent_table: The name of the parent table.
        Example: mytable
        :param db: The name of the database. 
        Example: demo
        :param partition: The name of the partition. If none is provided, it will remove all replicated partitions from the replication set.
        Example: mytable_202012
    """
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.repset_remove_partition(" + get_eq("parent", parent_table, "")
    if partition:
        sql = sql + "," + get_eq("partition", partition, "")
    sql = sql + ")"
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_list_tables(schema, db, pg=None):
    """List tables in replication sets.

        List all tables in all replication sets. \n
        Example: spock repset-list-tables '*' demo 
        :param schema: The name of the schema to list tables from. To list tables matching a pattern use single quotes and * as a wildcard.
        Examples: '*', mytable, 'my*'
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)

    sql = "SELECT * FROM spock.tables"
    if schema != "*":
        sql = sql + " WHERE nspname='" + schema + "'"
    sql = sql + " ORDER BY set_name, nspname, relname;"

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_create(
    subscription_name,
    provider_dsn,
    db,
    replication_sets=("default", "default_insert_only", "ddl_sql"),
    synchronize_structure=False,
    synchronize_data=False,
    forward_origins="",
    apply_delay=0,
    pg=None,
):
    """Create a subscription.

        Create a subscription. \n
        Example: spock sub-create sub_n2n1 'host=10.1.2.5 port=5432 user=pgedge dbname=demo' demo
        :param subscription_name: The name of the subscription. Each subscription in a cluster must have a unique name.
        Example: sub_n2n1
        :param provider_dsn: The connection string to the node that this node will subscribe to.
        The user in this string should equal the OS user. 
        This connection string should be reachable from this node and match the one used previously in the node-create command. 
        Example: 'host=10.1.2.5 port= 5432 user=pgedge dbname=demo'
        :param db: The name of the database. 
        Example: demo
        :param replication_sets: An array of replication sets to automatically include in this subscription. 
        Example: 'demo_repset,default,default_insert_only,ddl_sql'
        :param synchronize_structure: Synchronize structure on subscription create. If some objects already exist in this database then the create of the subscription will fail.
        :param synchronize_data: Synchronize data on subscription create.
        :param forward_origins: For multimaster, this should be kept at the default. For replicating everything written to a node, transactions replicated to it included, this can be set to 'all'. 
        :param apply_delay: The amount of time to delay the replication.
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_create("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("provider_dsn", provider_dsn, ", ")
    )
    if "," in str(replication_sets):
        sql = sql + get_eq("replication_sets", ",".join(replication_sets), ", ", True)
    else:
        sql = sql + get_eq("replication_sets", replication_sets, ", ", True)
    sql = (
        sql
        + get_eq("synchronize_structure", synchronize_structure, ", ")
        + get_eq("synchronize_data", synchronize_data, ", ")
        + get_eq("forward_origins", str(forward_origins), ", ", True)
        + get_eq("apply_delay", apply_delay, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_drop(subscription_name, db, pg=None):
    """Delete a subscription.
        
        Drop a subscription. \n
        Example: spock sub-drop sub_n2n1 demo
        :param subscription_name: The name of the subscription.
        Example: sub_n2n1
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.sub_drop(" + get_eq("subscription_name", subscription_name, ")")
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_enable(subscription_name, db, immediate=False, pg=None):
    """Make a subscription live.

        Enable a subscription. \n
        Example: spock sub-enable sub_n2n1 demo
        :param subscription_name: The name of the subscription.
        Example: sub_n2n1
        :param db: The name of the database. 
        Example: demo
        :param immediate: If False, sub will start after the current transaction. 
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_enable("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("immediate", immediate, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_disable(subscription_name, db, immediate=False, pg=None):
    """Put a subscription on hold and disconnect from provider.
   
        Disable a subscription by putting it on hold and disconnect from provider. \n
        Example: spock sub-disable sub_n2n1 demo
        :param subscription_name: The name of the subscription.
        Example: sub_n2n1
        :param db: The name of the database. 
        Example: demo
        :param immediate: If False, sub will stop after the current transaction. 
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_disable("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("immediate", immediate, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_alter_interface(subscription_name, interface_name, db, pg=None):
    """Modify an interface to a subscription.

        Alter the subscription to use a different interface when connecting to the provider node. \n
        Example: spock sub-alter-interface sub_n2n1 n1_2 demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param interface_name: The interface name to add to the node.
        Should match an interface name already created on the provider node.
        Example: n1_2
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_alter_interface("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("interface_name", interface_name, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_show_status(subscription_name, db, pg=None):
    """Display the status of the subscription.

        Show the status and basic information of a subscription. \n
        Example: spock sub-show-status sub_n2n1 demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)

    sql = "SELECT spock.sub_show_status("
    if subscription_name != "*":
        sql = sql + get_eq("subscription_name", subscription_name, "")
    sql = sql + ")"

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_show_table(subscription_name, relation, db, pg=None):
    """Show subscription tables.
        
        Shows synchronization status of a table. \n
        Example: spock sub-show-table sub_n2n1 mytable demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param relation: Table name. 
        Example: mytable
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)

    sql = (
        "SELECT spock.sub_show_table("
        + get_eq("subscription_name", subscription_name, ", ")
        + "relation := '"
        + relation
        + "'::regclass)"
    )

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_resync_table(subscription_name, relation, db, truncate=False, pg=None):
    """Resynchronize a table.
    
        Resynchronize one existing table. \n
        Example: spock sub-resync-table sub_n2n1 mytable demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param relation: Table name. 
        Example: mytable
        :param db: The name of the database. 
        Example: demo
        :param truncate: WARNING: If this is set to True, the function will truncate the table immediately, and only then begin synchronising it, so it will be empty while being synced.
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_resync_table("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("relation", relation, ", ")
        + get_eq("truncate", truncate, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_add_repset(subscription_name, replication_set, db, pg=None):
    """Add a replication set to a subscription.

        Add a replication set to a subscription. \n
        Example: spock sub-add-repset sub_n2n1 demo_repset demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param replication_set: Name of a replication set. 
        Example: demo_repset
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)

    sql = (
        "SELECT spock.sub_add_repset("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("replication_set", replication_set, ")")
    )

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_remove_repset(subscription_name, replication_set, db, pg=None):
    """Drop a replication set from a subscription.

        Remove a replication set from a subscription. \n
        Example: spock sub-remove-repset sub_n2n1 demo_repset demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param replication_set: Name of a replication set. 
        Example: demo_repset
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.sub_remove_repset("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("replication_set", replication_set, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def table_wait_for_sync(subscription_name, relation, db, pg=None):
    """Pause until a table finishes synchronizing.
    
        Pause until a table finishes synchronizing. \n
        Example: spock table-wait-for-sync sub_n2n1 mytable demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param relation: The name of a table. 
        Example: mytable
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)

    sql = (
        "SELECT spock.table_wait_for_sync("
        + get_eq("subscription_name", subscription_name, ", ")
        + get_eq("relation", relation, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sub_wait_for_sync(subscription_name, db, pg=None):
    """Pause until the subscription is synchronized.
        
        Wait for a subscription to finish synchronization after a sub create or sub sync command. \n
        Example: spock sub-wait-for-sync sub_n2n1 demo
        :param subscription_name: The name of the subscription. 
        Example: sub_n2n1
        :param db: The name of the database. 
        Example: demo
    """

    pg_v = util.get_pg_v(pg)

    sql = "SELECT spock.sub_wait_for_sync(" + get_eq(
        "subscription_name", subscription_name, ")"
    )

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def set_readonly(readonly="off", pg=None):
    """Turn PG read-only mode 'on' or 'off'."""

    if readonly not in ("on", "off"):
        util.exit_message("  readonly flag must be 'off' or 'on'")

    pg_v = util.get_pg_v(pg)

    try:
        con = util.get_pg_connection(pg_v, "postgres", util.get_user())
        cur = con.cursor(row_factory=psycopg.rows.dict_row)

        util.change_pgconf_keyval(pg_v, "default_transaction_read_only", readonly, True)

        util.message("reloading postgresql.conf")
        cur.execute("SELECT pg_reload_conf()")
        cur.close()
        con.close()

    except Exception as e:
        util.exit_exception(e)

    sys.exit(0)


def get_pii_cols(db, schema=None, pg=None):
    """Retrieve the columns that you have identified as PII"""

    pg_v = util.get_pg_v(pg)

    if schema is None:
        schema = "public"
    sql = (
        "SELECT pii_table, pii_column FROM spock.pii WHERE pii_schema='"
        + schema
        + "' ORDER BY pii_table;"
    )

    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def repset_add_table(
    replication_set,
    table,
    db,
    synchronize_data=False,
    columns=None,
    row_filter=None,
    include_partitions=True,
    pg=None,
):
    """Add table(s) to a replication set.

        Add a table or tables to a replication set. \n
        Example: spock repset-add-table demo_repset 'public.*' demo
        :param replication_set: The replication set name.
        Example: demo_repset
        :param table: The name of the table(s) to add. To add all tables matching a pattern use single quotes and * as a wildcard.
        Examples: '*', mytable, 'public.*'
        :param db: The name of the database. 
        Example: demo
        :param synchronize_data: Synchronized table data on all related subscribers.
        :param columns: list of columns to replicate.
        Example: 'my_id, col_1, col_2'
        :param row_filter: Row filtering expression.
        Example: 'my_id = 1001'
        :param include_partitions: include all partitions in replication.
    """
    pg_v = util.get_pg_v(pg)
    tbls = util.get_table_list(table, db, pg_v)
    con = util.get_pg_connection(pg_v, db, util.get_user())

    for tbl in tbls:
        tab = str(tbl[0])
        sql = (
            "SELECT spock.repset_add_table("
            + get_eq("set_name", replication_set, ", ")
            + get_eq("relation", tab, ", ")
            + get_eq("synchronize_data", synchronize_data, ", ")
        )

        if columns and len(tbls) == 1:
            sql = sql + get_eq("columns", ",".join(columns), ", ", True)

        if row_filter and len(tbls) == 1:
            sql = sql + get_eq("row_filter", row_filter, ", ")

        sql = sql + get_eq("include_partitions", include_partitions, ") ")
        util.message(f"Adding table {tab} to replication set {replication_set}.")

        try:
            con.transaction()
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
        except Exception as e:
            util.print_exception(e, "warning")
            con.rollback()

    sys.exit(0)


def repset_remove_table(replication_set, table, db, pg=None):
    """Remove table from replication set.
    
        Remove a table from a replication set. \n
        Example: spock repset-remove-table demo_repset public.mytable demo
        :param replication_set: The replication set name.
        Example: demo_repset
        :param table: The name of the table to remove. 
        Examples:  public.mytable
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    sql = (
        "SELECT spock.repset_remove_table("
        + get_eq("set_name", replication_set, ", ")
        + get_eq("relation", table, ")")
    )
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def sequence_convert(sequence, db, type="snowflake", pg=None):
    """Convert sequence to snowflake sequence.
        
        Convert sequence(s) to snowflake sequences. \n
        Example: spock sequence-convert 'public.*' demo 
        :param sequence: The sequence name. To convert all sequences matching a pattern use single quotes and * as a wildcard.
        Examples: '*', myseq, 'public.*'
        :param db: The name of the database. 
        Example: demo
    """
    pg_v = util.get_pg_v(pg)
    seqs = util.get_seq_list(sequence, db, pg_v)
    con = util.get_pg_connection(pg_v, db, util.get_user())

    for sequence in seqs:
        seq = str(sequence[0])
        sql = f"SELECT spock.convert_sequence_to_snowflake('{seq}')"
        util.message(f"Converting sequence {seq} to {type} sequence.")
        try:
            con.transaction()
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
        except Exception as e:
            util.print_exception(e, "warning")
            con.rollback()

    sys.exit(0)


def replicate_ddl(replication_sets, sql_command, db, pg=None):
    """Replicate DDL through replication set(s).

        Replicate DDL statement through replication set(s) \n
        Example: spock replicate-ddl demo_repset "CREATE TABLE public.mytable (a INT PRIMARY KEY, b INT)" demo
        :param replication_sets: One or more replication sets to replicate the ddl command to.
        Example: demo_repset, 'demo_repset,default'
        :param sql_command: The SQL command to replicate. Use schema and object name. 
        Example: "CREATE TABLE public.mytable (a INT PRIMARY KEY, b INT)"
        :param db: The name of the database. 
        Example: demo 
    """
    pg_v = util.get_pg_v(pg)
    sql = "SELECT spock.replicate_ddl(" + get_eq("command", sql_command, ", ")
    if "," in str(replication_sets):
        sql = sql + get_eq("replication_sets", ",".join(replication_sets), ")", True)
    else:
        sql = sql + get_eq("replication_sets", replication_sets, ")", True)
    util.run_psyco_sql(pg_v, db, sql)
    sys.exit(0)


def health_check(pg=None):
    """Check if PG instance is accepting connections."""
    pg_v = util.get_pg_v(pg)

    if util.is_pg_ready(pg_v):
        util.exit_message("True", 0)

    util.exit_message("false", 0)


def metrics_check(db, pg=None):
    """Retrieve advanced DB & OS metrics."""
    try:
        import psutil
    except ImportError:
        util.exit_message("Missing or bad psutil module", 1)

    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    rc = util.is_pg_ready(pg_v)

    load1, load5, load15 = psutil.getloadavg()

    cpu_pct_lst = psutil.cpu_times_percent(interval=0.3, percpu=False)
    cpu_pct = round(cpu_pct_lst.user + cpu_pct_lst.system, 1)
    if cpu_pct < 0.05:
        # test again after a little rest
        time.sleep(1)
        cpu_pct_lst = psutil.cpu_times_percent(interval=0.3, percpu=False)
        cpu_pct = round(cpu_pct_lst.user + cpu_pct_lst.system, 1)

    disk = psutil.disk_io_counters(perdisk=False)
    disk_read_mb = round((disk.read_bytes / 1024 / 1024), 1)
    disk_write_mb = round((disk.write_bytes / 1024 / 1024), 1)

    disk_mount_pt = ""
    disk_size = ""
    disk_used = ""
    disk_avail = ""
    disk_used_pct = ""

    try:
        dfh = str(subprocess.check_output("df -h | grep '/data$'", shell=True)).split()
        if len(dfh) >= 5:
            disk_mount_pt = "/data"
            disk_size = str(dfh[1])
            disk_used = str(dfh[2])
            disk_avail = str(dfh[3])
            disk_used_pct = float(util.remove_suffix("%", str(dfh[4])))
    except Exception:
        try:
            dfh = str(subprocess.check_output("df -h | grep '/$'", shell=True)).split()
            if len(dfh) >= 5:
                disk_mount_pt = "/"
                disk_size = str(dfh[1])
                disk_used = str(dfh[2])
                disk_avail = str(dfh[3])
                disk_used_pct = float(util.remove_suffix("%", str(dfh[4])))
        except Exception:
            pass

    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute(
            "SELECT setting FROM pg_settings WHERE name = 'default_transaction_read_only'"
        )
        data = cur.fetchone()
        readonly = str(data[0])
        cur.close()
    except Exception as e:
        util.print_exception(e, "warning")
        con.rollback()

    mtrc_dict = {
        "pg_isready": rc,
        "readonly": readonly,
        "cpu_pct": cpu_pct,
        "load_avg": [load1, load5, load15],
        "disk": {
            "read_mb": disk_read_mb,
            "write_mb": disk_write_mb,
            "size": disk_size,
            "used": disk_used,
            "available": disk_avail,
            "used_pct": disk_used_pct,
            "mount_point": disk_mount_pt,
        },
    }
    if rc is False:
        return util.json_dumps(mtrc_dict)

    try:
        cur = con.cursor()
        cur.execute("SELECT count(*) as resolutions FROM spock.resolutions")
        data = cur.fetchone()
        rsltns = data[0]
        cur.close()
        mtrc_dict.update({"resolutions": rsltns})

        mtrc_dict.update({"slots": []})
        cur = con.cursor()
        sql_slots = (
            "SELECT slot_name, commit_lsn, commit_timestamp, "
            + "replication_lag, replication_lag_bytes "
            + "FROM spock.lag_tracker ORDER BY slot_name"
        )
        cur.execute(sql_slots)
        for row in cur:
            mtrc_dict["slots"].append(
                {
                    "slot_name": row[0],
                    "commit_lsn": str(row[1]),
                    "commit_timestamp": str(row[2]),
                    "replication_lag": str(row[3]),
                    "replication_lag_bytes": str(row[4]),
                }
            )
        cur.close()

    except Exception:
        pass

    return util.json_dumps(mtrc_dict)


if __name__ == "__main__":
    fire.Fire(
        {
            "node-create": node_create,
            "node-drop": node_drop,
            "node-alter-location": node_alter_location,
            "node-list": node_list,
            "node-add-interface": node_add_interface,
            "node-drop-interface": node_drop_interface,
            "repset-create": repset_create,
            "repset-alter": repset_alter,
            "repset-drop": repset_drop,
            "repset-add-table": repset_add_table,
            "repset-remove-table": repset_remove_table,
            "repset-add-seq": repset_add_seq,
            "repset-remove-seq": repset_remove_seq,
            "repset-add-partition": repset_add_partition,
            "repset-remove-partition": repset_remove_partition,
            "repset-list-tables": repset_list_tables,
            "sub-create": sub_create,
            "sub-drop": sub_drop,
            "sub-alter-interface": sub_alter_interface,
            "sub-enable": sub_enable,
            "sub-disable": sub_disable,
            "sub-add-repset": sub_add_repset,
            "sub-remove-repset": sub_remove_repset,
            "sub-show-status": sub_show_status,
            "sub-show-table": sub_show_table,
            "sub-resync-table": sub_resync_table,
            "sub-wait-for-sync": sub_wait_for_sync,
            "table-wait-for-sync": table_wait_for_sync,
            "replicate-ddl": replicate_ddl,
            "sequence-convert": sequence_convert,
            "health-check": health_check,
            "metrics-check": metrics_check,
            "set-readonly": set_readonly,
        }
    )

