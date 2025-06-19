from datetime import datetime
import json
import traceback
import ace_config as config
import ace_core
import ace_daemon
import ace_db
from ace_data_models import (
    RepsetDiffTask,
    SchemaDiffTask,
    SpockDiffTask,
    TableDiffTask,
    TableRepairTask,
    MerkleTreeTask,
)
import ace
import ace_mtree
import util
from ace_exceptions import AceException


class MerkleTreeCLI(object):
    """
    Use Merkle Trees for efficient table diffs.

    Use Merkle Trees for efficient table diffs.
    """

    """
    Initialises the MarkleTreeCLI and sets up command groups.
    This allows it to behave like another module under ace
    """
    def __init__(self):
        self._commands = {
            "init": self.init,
            "build": self.build,
            "update": self.update,
            "table-diff": self.table_diff,
            "teardown": self.teardown,
        }
    
    def __getattr__(self, name):
        try:
            return self._commands[name]
        except KeyError:
            raise AttributeError(f"No such command: {name}")

    def __dir__(self):
        # Allows Fire to generate proper helptext using dash-case commands
        return list(self._commands.keys())
        
    def _execute_task(self, mode, **kwargs):
        """Helper to run merkle tree tasks."""
        task_id = ace_db.generate_task_id()

        try:
            mtree_task = MerkleTreeTask(
                mode=mode,
                cluster_name=kwargs.get("cluster_name"),
                _table_name=kwargs.get("table_name"),
                _dbname=kwargs.get("dbname"),
                analyse=kwargs.get("analyse", False),
                rebalance=kwargs.get("rebalance", False),
                recreate_objects=kwargs.get("recreate_objects", False),
                block_size=kwargs.get("block_size", config.MTREE_BLOCK_SIZE),
                max_cpu_ratio=kwargs.get("max_cpu_ratio", config.MAX_CPU_RATIO),
                batch_size=kwargs.get("batch_size", 1),
                output=kwargs.get("output", "json"),
                quiet_mode=kwargs.get("quiet_mode", False),
                write_ranges=kwargs.get("write_ranges", False),
                ranges_file=kwargs.get("ranges_file"),
                _nodes=kwargs.get("nodes", "all"),
                invoke_method="cli",
            )
            mtree_task.scheduler.task_id = task_id
            mtree_task.scheduler.task_type = f"mtree-{mode}"
            mtree_task.scheduler.task_status = "RUNNING"
            mtree_task.scheduler.started_at = datetime.now()

            override_block_size = kwargs.get("override_block_size", False)

            if ((mode == "teardown") and (not kwargs.get("table_name"))) or (
                mode == "init"
            ):
                ace.validate_merkle_tree_inputs(
                    mtree_task,
                    skip_table_check=True,
                    override_block_size=override_block_size,
                )
            else:
                ace.validate_merkle_tree_inputs(
                    mtree_task, override_block_size=override_block_size
                )

            ace_db.create_ace_task(task=mtree_task)

            if mode == "init":
                ace_mtree.mtree_init_helper(mtree_task)
            elif mode == "build":
                ace_mtree.build_mtree(mtree_task)
            elif mode == "update":
                ace_mtree.update_mtree(mtree_task)
            elif mode == "table-diff":
                ace_mtree.merkle_tree_diff(mtree_task)
            elif mode == "teardown":
                ace_mtree.mtree_teardown_helper(mtree_task)

            mtree_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running merkle tree: {e}")

    def init(self, cluster_name, dbname=None, nodes="all", quiet_mode=False):
        """
        Initialises the database with necessary objects for Merkle trees.

        Args:
            cluster_name (str): Name of the cluster.
            dbname (str, optional): Name of the database.
            nodes (str, optional): Comma-separated subset of nodes.
            quiet_mode (bool, optional): Suppress output.
        """
        self._execute_task(
            "init",
            cluster_name=cluster_name,
            dbname=dbname,
            nodes=nodes,
            quiet_mode=quiet_mode,
        )

    def build(
        self,
        cluster_name,
        table_name,
        dbname=None,
        analyse=False,
        recreate_objects=False,
        block_size=config.MTREE_BLOCK_SIZE,
        max_cpu_ratio=config.MAX_CPU_RATIO,
        write_ranges=False,
        ranges_file=None,
        nodes="all",
        quiet_mode=False,
        override_block_size=False,
    ):
        """
        Builds a new Merkle tree for a table.

        Args:
            cluster_name (str): Name of the cluster.
            table_name (str): Schema-qualified table name.
            dbname (str, optional): Name of the database.
            analyse (bool, optional): Run ANALYZE on the table.
            recreate_objects (bool, optional): Drop and recreate Merkle tree objects.
            block_size (int, optional): Rows per leaf block.
            max_cpu_ratio (float, optional): Max CPU for parallel operations.
            write_ranges (bool, optional): Write block ranges to a JSON file.
            ranges_file (str, optional): Path to a file with pre-computed ranges.
            nodes (str, optional): Comma-separated subset of nodes.
            quiet_mode (bool, optional): Suppress output.
            override_block_size (bool, optional): Allow unsafe block size.
        """
        self._execute_task(
            "build",
            cluster_name=cluster_name,
            table_name=table_name,
            dbname=dbname,
            analyse=analyse,
            recreate_objects=recreate_objects,
            block_size=block_size,
            max_cpu_ratio=max_cpu_ratio,
            write_ranges=write_ranges,
            ranges_file=ranges_file,
            nodes=nodes,
            quiet_mode=quiet_mode,
            override_block_size=override_block_size,
        )

    def update(
        self,
        cluster_name,
        table_name,
        dbname=None,
        rebalance=False,
        max_cpu_ratio=config.MAX_CPU_RATIO,
        nodes="all",
        quiet_mode=False,
    ):
        """
        Updates an existing Merkle tree.

        Args:
            cluster_name (str): Name of the cluster.
            table_name (str): Schema-qualified table name.
            dbname (str, optional): Name of the database.
            rebalance (bool, optional): Trigger rebalancing of the tree.
            max_cpu_ratio (float, optional): Max CPU for parallel operations.
            nodes (str, optional): Comma-separated subset of nodes.
            quiet_mode (bool, optional): Suppress output.
        """
        self._execute_task(
            "update",
            cluster_name=cluster_name,
            table_name=table_name,
            dbname=dbname,
            rebalance=rebalance,
            max_cpu_ratio=max_cpu_ratio,
            nodes=nodes,
            quiet_mode=quiet_mode,
        )

    def table_diff(
        self,
        cluster_name,
        table_name,
        dbname=None,
        rebalance=False,
        max_cpu_ratio=config.MAX_CPU_RATIO,
        batch_size=1,
        nodes="all",
        output="json",
        quiet_mode=False,
    ):
        """
        Compares Merkle trees of a table across cluster nodes.

        Args:
            cluster_name (str): Name of the cluster.
            table_name (str): Schema-qualified table name.
            dbname (str, optional): Name of the database.
            max_cpu_ratio (float, optional): Max CPU for parallel operations.
            batch_size (int, optional): Number of blocks per worker batch.
            nodes (str, optional): Comma-separated subset of nodes.
            output (str, optional): Output format (json, csv, html).
            quiet_mode (bool, optional): Suppress output.
        """
        self._execute_task(
            "table-diff",
            cluster_name=cluster_name,
            table_name=table_name,
            dbname=dbname,
            rebalance=rebalance,
            max_cpu_ratio=max_cpu_ratio,
            batch_size=batch_size,
            nodes=nodes,
            output=output,
            quiet_mode=quiet_mode,
        )

    def teardown(
        self, cluster_name, table_name=None, dbname=None, nodes="all", quiet_mode=False
    ):
        """
        Removes Merkle tree objects.

        Args:
            cluster_name (str): Name of the cluster.
            table_name (str, optional): Schema-qualified table name. If omitted,
                removes objects for the entire database.
            dbname (str, optional): Name of the database.
            nodes (str, optional): Comma-separated subset of nodes.
            quiet_mode (bool, optional): Suppress output.
        """
        self._execute_task(
            "teardown",
            cluster_name=cluster_name,
            table_name=table_name,
            dbname=dbname,
            nodes=nodes,
            quiet_mode=quiet_mode,
        )


class TableDiffCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        table_name,
        dbname=None,
        block_size=config.DIFF_BLOCK_SIZE,
        max_cpu_ratio=config.MAX_CPU_RATIO,
        output="json",
        nodes="all",
        batch_size=config.DIFF_BATCH_SIZE,
        table_filter=None,
        quiet=False,
        override_block_size=False,
    ):
        """
        Compare a table across a cluster and produce a report showing
        differences, if any.

        Args:
            cluster_name (str): Name of the cluster where the operation should be
                performed.
            table_name (str): Schema-qualified name of the table that you are
                comparing across cluster nodes.
            dbname (str, optional): Name of the database to use. If omitted,
                defaults to the first database in the cluster configuration file.
            block_size (int, optional): Number of rows to process per block.
                Defaults to config.DIFF_BLOCK_SIZE.
            max_cpu_ratio (float, optional): Maximum CPU utilisation. The accepted
                range is 0.0-1.0. Defaults to config.MAX_CPU_RATIO_DEFAULT.
            output (str, optional): Output format. Acceptable values are "json",
                "csv", and "html". Defaults to "json".
            nodes (str, optional): Comma-separated subset of nodes on which the
                command will be executed. Defaults to "all".
            batch_size (int, optional): Size of each batch, i.e., number of blocks
                each worker should process. Defaults to config.DIFF_BATCH_SIZE.
            table_filter (str, optional): Used to compare a subset of rows in the table.
                Specified as a WHERE clause of a SQL query. E.g.,
                --table-filter="customer_id < 100" will compare only rows with
                customer_id less than 100.  If omitted, the entire table is compared.
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.
            override_block_size (bool, optional): Allow unsafe block size. Defaults
                to False.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the table diff operation.

        Returns:
            None. The function performs the table diff operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            td_task = TableDiffTask(
                cluster_name=cluster_name,
                _table_name=table_name,
                _dbname=dbname,
                block_size=block_size,
                max_cpu_ratio=max_cpu_ratio,
                output=output,
                _nodes=nodes,
                batch_size=batch_size,
                quiet_mode=quiet,
                table_filter=table_filter,
                invoke_method="cli",
                _override_block_size=override_block_size,
            )
            td_task.scheduler.task_id = task_id
            td_task.scheduler.task_type = "table-diff"
            td_task.scheduler.task_status = "RUNNING"
            td_task.scheduler.started_at = datetime.now()

            ace.validate_table_diff_inputs(td_task)
            ace_db.create_ace_task(task=td_task)
            ace_core.table_diff(td_task)
            td_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running table diff: {e}")


class TableRepairCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        table_name,
        diff_file,
        source_of_truth=None,
        dbname=None,
        dry_run=False,
        quiet=False,
        generate_report=False,
        insert_only=False,
        upsert_only=False,
        fix_nulls=False,
        fire_triggers=False,
        bidirectional=False,
    ):
        """
        Repair a table across a cluster by fixing data inconsistencies identified
        in a table-diff operation.

        Args:
            cluster_name (str): Name of the cluster where the operation should be
                performed.
            diff_file (str): Path to the diff file generated by a previous table diff.
            source_of_truth (str): Node name to be used as the source of truth for
                the repair.
            table_name (str): Schema-qualified name of the table that you are
                comparing across cluster nodes.
            dbname (str, optional): Name of the database. Defaults to the name of
                the first database in the cluster configuration.
            dry_run (bool, optional): If True, simulates the repair without making
                changes. Defaults to False.
            generate_report (bool, optional): If True, generates a detailed report
                of the repair. Defaults to False.
            upsert_only (bool, optional): If True, only performs upsert operations,
                skipping deletions. Defaults to False.
            insert_only (bool, optional): If True, only performs insert operations,
                skipping updates and deletions.
            fix_nulls (bool, optional): If True, fixes null values in the table
                columns by looking at the corresponding column in the other nodes.
                Does not need the source of truth to be specified. Must be used
                only in special cases. This is not a recommended option for
                repairing divergence. Defaults to False.
            fire_triggers (bool, optional): If True, fires triggers on a table, if any,
                during the repair process. Note that ENABLE ALWAYS triggers will fire
                regardless of the value.
            bidirectional (bool, optional): If True, performs a bidirectional
                repair, applies differences found between nodes to create a
                distinct union of the content. In a distinct union, each row that
                is missing is recreated on the node from which it is missing,
                eventually leading to a data set (on all nodes) in which all rows
                are represented exactly once.
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the table repair operation.

        Returns:
            None. The function performs the table repair operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            tr_task = TableRepairTask(
                cluster_name=cluster_name,
                diff_file_path=diff_file,
                source_of_truth=source_of_truth,
                _table_name=table_name,
                _dbname=dbname,
                dry_run=dry_run,
                quiet_mode=quiet,
                generate_report=generate_report,
                insert_only=insert_only,
                upsert_only=upsert_only,
                fix_nulls=fix_nulls,
                fire_triggers=fire_triggers,
                bidirectional=bidirectional,
                invoke_method="cli",
            )
            tr_task.scheduler.task_id = task_id
            tr_task.scheduler.task_type = "table-repair"
            tr_task.scheduler.task_status = "RUNNING"
            tr_task.scheduler.started_at = datetime.now()

            ace.validate_table_repair_inputs(tr_task)
            ace_db.create_ace_task(task=tr_task)

            if fix_nulls:
                ace_core.table_repair_fix_nulls(tr_task)
            elif bidirectional:
                ace_core.table_repair_bidirectional(tr_task)
            else:
                ace_core.table_repair(tr_task)

            tr_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running table repair: {e}")


class TableRerunCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        diff_file,
        table_name,
        dbname=None,
        quiet=False,
    ):
        """
        Rerun a table diff operation based on a previous diff file.

        Args:
            cluster_name (str): Name of the cluster where the operation should be
                performed.
            diff_file (str): Path to the diff file from a previous table diff
                operation.
            table_name (str): Schema-qualified name of the table that you are
                comparing across cluster nodes.
            dbname (str, optional): Name of the database to use. If omitted,
                defaults to the first database in the cluster configuration.
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the table rerun operation.

        Returns:
            None. The function performs the table rerun operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            td_task = TableDiffTask(
                cluster_name=cluster_name,
                _table_name=table_name,
                _dbname=dbname,
                block_size=config.DIFF_BLOCK_SIZE,
                max_cpu_ratio=config.MAX_CPU_RATIO,
                output="json",
                _nodes="all",
                batch_size=config.DIFF_BATCH_SIZE,
                table_filter=None,
                quiet_mode=quiet,
                diff_file_path=diff_file,
                invoke_method="cli",
            )
            td_task.scheduler.task_id = task_id
            td_task.scheduler.task_type = "table-rerun"
            td_task.scheduler.task_status = "RUNNING"
            td_task.scheduler.started_at = datetime.now()

            ace.validate_table_diff_inputs(td_task)
            ace_db.create_ace_task(task=td_task)
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running table rerun: {e}")

        try:
            ace_core.table_rerun_temptable(td_task)
            td_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running table rerun: {e}")


class RepsetDiffCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        repset_name,
        dbname=None,
        block_size=config.DIFF_BLOCK_SIZE,
        max_cpu_ratio=config.MAX_CPU_RATIO,
        output="json",
        nodes="all",
        batch_size=config.DIFF_BATCH_SIZE,
        quiet=False,
        skip_tables=None,
        skip_file=None,
    ):
        """
        Compare a repset across a cluster and produce a report showing
        any differences.

        Args:
            cluster_name (str): Name of the cluster where the operation should be
                performed.
            repset_name (str): Name of the repset to compare across cluster nodes.
            dbname (str, optional): Name of the database to use. If omitted,
                defaults to the first database in the cluster configuration.
            block_size (int, optional): Number of rows to process per block.
                Defaults to config.DIFF_BLOCK_SIZE.
            max_cpu_ratio (float, optional): Maximum CPU utilisation. The accepted
                range is 0.0-1.0. Defaults to config.MAX_CPU_RATIO_DEFAULT.
            output (str, optional): Output format. Acceptable values are "json",
                "csv", and "html". Defaults to "json".
            nodes (str, optional): Comma-separated subset of nodes on which the
                command will be executed. Defaults to "all".
            batch_size (int, optional): Size of each batch, i.e., number of blocks
                each worker should process. Defaults to config.DIFF_BATCH_SIZE.
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.
            skip_tables (list, optional): Comma-separated list of tables to skip.
                If omitted, no tables are skipped.
            skip_file (str, optional): Path to a file containing a list of tables to
                skip. If omitted, no tables are skipped.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the repset diff operation.

        Returns:
            None. The function performs the repset diff operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            rd_task = RepsetDiffTask(
                cluster_name=cluster_name,
                _dbname=dbname,
                repset_name=repset_name,
                block_size=block_size,
                max_cpu_ratio=max_cpu_ratio,
                output=output,
                _nodes=nodes,
                batch_size=batch_size,
                quiet_mode=quiet,
                invoke_method="cli",
                skip_tables=skip_tables,
                skip_file=skip_file,
            )
            rd_task.scheduler.task_id = task_id
            rd_task.scheduler.task_type = "repset-diff"
            rd_task.scheduler.task_status = "RUNNING"
            rd_task.scheduler.started_at = datetime.now()

            ace.validate_repset_diff_inputs(rd_task)
            ace_db.create_ace_task(task=rd_task)
            ace_core.multi_table_diff(rd_task)

            # TODO: Figure out a way to handle repset-level connection pooling
            # This close_all() is redundant currently
            rd_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running repset diff: {e}")


class SchemaDiffCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        schema_name,
        nodes="all",
        dbname=None,
        ddl_only=True,
        skip_tables=None,
        skip_file=None,
        quiet=False,
    ):
        """
        Compare a schema across a cluster and produce a report showing
        any differences.

        Args:
            cluster_name (str): Name of the cluster where the operation should
                be performed.
            schema_name (str): Name of the schema that you are comparing across
                cluster nodes.
            nodes (str, optional): Comma-delimited subset of nodes on which the
                command will be executed. Defaults to "all".
            dbname (str, optional): Name of the database. Defaults to the name of
                the first database in the cluster configuration.
            ddl_only (bool, optional): If True, only compares DDL differences
                across nodes.
            skip_tables (list, optional): Comma-delimited list of tables to skip.
            skip_file (str, optional): Path to a file containing a list of tables
                to skip.
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the schema diff operation.

        Returns:
            None. The function performs the schema diff operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            sc_task = SchemaDiffTask(
                cluster_name=cluster_name,
                schema_name=schema_name,
                _dbname=dbname,
                _nodes=nodes,
                ddl_only=ddl_only,
                skip_tables=skip_tables,
                skip_file=skip_file,
                quiet_mode=quiet,
                invoke_method="cli",
            )
            sc_task.scheduler.task_id = task_id
            sc_task.scheduler.task_type = "schema-diff"
            sc_task.scheduler.task_status = "RUNNING"
            sc_task.scheduler.started_at = datetime.now()

            ace.schema_diff_checks(sc_task)
            ace_db.create_ace_task(task=sc_task)
            if ddl_only:
                ace_core.schema_diff_objects(sc_task)
            else:
                ace_core.multi_table_diff(sc_task)
            sc_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running schema diff: {e}")


class SpockDiffCLI(object):

    def __init__(self):
        pass

    def run(
        self,
        cluster_name,
        dbname=None,
        nodes="all",
        quiet=False,
    ):
        """
        Compare the spock metadata across a cluster and produce a report showing
        any differences.

        Args:
            cluster_name (str): Name of the cluster where the operation should be
                performed.
            dbname (str, optional): Name of the database. Defaults to the name of
                the first database in the cluster configuration.
            nodes (str, optional): Comma-delimited subset of nodes on which the
                command will be executed. Defaults to "all".
            quiet (bool, optional): Whether to suppress output in stdout. Defaults
                to False.

        Raises:
            AceException: If there's an error specific to the ACE operation.
            Exception: For any unexpected errors during the spock diff operation.

        Returns:
            None. The function performs the spock diff operation and handles any
            exceptions. All output messages are printed to stdout since it's a CLI
            function.
        """
        task_id = ace_db.generate_task_id()

        try:
            sd_task = SpockDiffTask(
                cluster_name=cluster_name,
                _dbname=dbname,
                _nodes=nodes,
                quiet_mode=quiet,
                invoke_method="cli",
            )
            sd_task.scheduler.task_id = task_id
            sd_task.scheduler.task_type = "spock-diff"
            sd_task.scheduler.task_status = "RUNNING"
            sd_task.scheduler.started_at = datetime.now()

            ace.validate_spock_diff_inputs(sd_task)
            ace_db.create_ace_task(task=sd_task)
            ace_core.spock_diff(sd_task)
            sd_task.connection_pool.close_all()
        except AceException as e:
            util.exit_message(str(e))
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running spock diff: {e}")


class SpockExceptionUpdateCLI(object):

    def __init__(self):
        pass

    def run(self, cluster_name, node_name, entry, dbname=None) -> None:
        """
        Update the Spock exception status for a specified cluster and node.

        Args:
            cluster_name (str): Name of the cluster where the operation should
                be performed.
            node_name (str): The name of the node within the cluster where the
                update should be performed.
            entry (str): A JSON string representing the exception entry. Should contain
                the following keys.

                    - "remote_origin" (str): Identifier of the origin node of the
                        transaction that caused the exception. (Required)

                    - "remote_commit_ts" (str): Commit timestamp of the
                        transaction on the remote origin. (Required)

                    - "remote_xid" (str): Transaction ID on the remote origin.
                        (Required)

                    - "status" (str): The new status to set for the exception (e.g.,
                        "RESOLVED", "IGNORED"). (Required)

                    - "resolution_details" (dict, optional): A JSON serialisable
                        dictionary containing details about the resolution.

                    - "command_counter" (int, optional): If specified, only the specific
                        exception detail (matching this command_counter along with
                        remote_origin, remote_commit_ts, remote_xid) in the
                        `spock.exception_status_detail` table is updated. If omitted,
                        the main entry in `spock.exception_status` and all related
                        detail entries for the (remote_origin, remote_commit_ts,
                        remote_xid) trio in `spock.exception_status_detail` are updated.
            dbname (str, optional): Name of the database. Defaults to the name of
                the first database in the cluster configuration.

        Raises:
            AceException: If an error specific to the ACE system occurs.
            json.JSONDecodeError: If the provided exception entry is not valid
                JSON.
            Exception: For any other unexpected errors.

        Returns:
            None
        """
        try:
            conn = ace.update_spock_exception_checks(
                cluster_name, node_name, entry, dbname
            )
            ace_core.update_spock_exception(entry, conn)
        except AceException as e:
            util.exit_message(str(e))
        except json.JSONDecodeError:
            util.exit_message("Exception entry is not a valid JSON")
        except Exception as e:
            traceback.print_exc()
            util.exit_message(f"Unexpected error while running exception status: {e}")

        util.message("Spock exception status updated successfully", p_state="success")


class StartCLI(object):
    def __init__(self):
        pass

    def run(self):
        """
        Start the ACE background scheduler and API.
        """
        ace_daemon.start_ace()


class AceCLI(object):
    """
    The Active Consistency Engine of pgEdge.
    """

    def __init__(self):
        """
        Initialises the AceCLI and sets up command groups.
        """
        self._commands = {
            "mtree": MerkleTreeCLI,
            "table-diff": TableDiffCLI().run,
            "table-repair": TableRepairCLI().run,
            "table-rerun": TableRerunCLI().run,
            "repset-diff": RepsetDiffCLI().run,
            "schema-diff": SchemaDiffCLI().run,
            "spock-diff": SpockDiffCLI().run,
            "spock-exception-update": SpockExceptionUpdateCLI().run,
            "start": StartCLI().run,
        }

    def __getattr__(self, name):
        try:
            return self._commands[name]
        except KeyError:
            raise AttributeError(f"No such command: {name}")

    def __dir__(self):
        # Allows Fire to generate proper helptext using dash-case commands
        return list(self._commands.keys())
