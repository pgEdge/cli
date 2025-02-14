# CLI Configuration

## Setting Parameter Values

*The parameters documented on this page apply to CLI users that will be using the CLI with the Spock or Snowflake extensions.*

The CLI uses parameter settings in the [postgresql.conf](https://www.postgresql.org/docs/16/config-setting.html#CONFIG-SETTING-CONFIGURATION-FILE) file to manage the replication behavior of PostgreSQL and the extensions that provide advanced functionality for pgEdge. 

Parameters are set to their default values when you install the CLI.  You can modify the parameter values later, but should consider the default values to be the minimum values required; we do not recommend lowering these values:

| Parameter Name | Valid/Default Settings and Description |
|----------------|-----------------|
| [hot_standby_feedback](https://www.postgresql.org/docs/16/runtime-config-replication.html#GUC-HOT-STANDBY-FEEDBACK) | `on`; this setting is required. |
| [max_worker_processes](https://www.postgresql.org/docs/16/runtime-config-resource.html#GUC-MAX-WORKER-PROCESSES) | `12`; this is the minimum value required. |
| [max_replication_slots](https://www.postgresql.org/docs/16/runtime-config-replication.html#GUC-MAX-REPLICATION-SLOTS) | `16`; this is the minimum value required. |
| [max_wal_senders](https://www.postgresql.org/docs/16/runtime-config-replication.html#GUC-MAX-WAL-SENDERS) | `16`; this is the minimum value required. |
| [shared_preload_libraries](https://www.postgresql.org/docs/16/runtime-config-client.html#GUC-SESSION-PRELOAD-LIBRARIES) | `pg_stat_statements`, `snowflake`, `spock`; include these values to use pgEdge replication features. |
| [snowflake.node](https://docs.pgedge.com/platform/advanced/snowflake) | The snowflake node number; this value is unique to each node. |
| [spock.allow_ddl_from_functions](https://except.pgedge-docs-sandbox.pages.dev/platform/advanced/autoddl) | `off`; Use this GUC to specify automatic ddl replication behavior. |
| [spock.conflict_resolution](https://docs.pgedge.com/spock_ext/guc_settings) | `conflict_resolution` sets the resolution method for any detected conflicts between local data and incoming changes.  `last_update_wins` (the newest commit timestamp will be retained) is the default value used by pgEdge. To use conflict resolution, enable `track_commit_timestamp` as well. |
| [spock.conflict_log_level](https://docs.pgedge.com/spock_ext/guc_settings) | The log level to use for logging conflicts; the default is: `DEBUG`. |
| [spock.enable_ddl_replication](https://except.pgedge-docs-sandbox.pages.dev/platform/advanced/autoddl) | `off`; Use this GUC to control automatic ddl replication behavior. |
| [spock.exception_behaviour](https://except.pgedge-docs-sandbox.pages.dev/platform/advanced/exception#spockexception_behaviour)| `discard`, `transdiscard`, or `sub-disable`; the default is `transdiscard` (if an error occurs, all operations are rolled back, regardless of succeeding or failing). Sub-disable disables the subscription for the node on which the exception was reported, and adds transactions for the disabled node to a queue that is written to the WAL log file; when the subscription is enabled, replication resumes with the transaction that caused the exception, followed by the other queued transactions. |
| [spock.exception_logging](https://except.pgedge-docs-sandbox.pages.dev/platform/advanced/exception#spockexception_logging)| `none`,`discard`, or `all` Use `spock.exception_logging` to specify a preference about logging exceptions when they occur.|
| [spock.include_ddl_repset](https://except.pgedge-docs-sandbox.pages.dev/platform/advanced/autoddl) | `off`; automatically add tables to replication sets at the time they are created on each node. |
| [spock.readonly](https://docs.pgedge.com/spock_ext/guc_settings) | `all`, `user`, or `off`.  The default of `off` means that the database is fully read/write. `user` means database can be updated by replication, but not by a client application. `all` means database is 100% read only and not even spock can modify it. Read only workloads are always allowed.  |
| [spock.save_resolutions](https://docs.pgedge.com/spock_ext/guc_settings) | `off`; log all conflict resolutions to the `spock.resolutions` table. This option can only be set when the postmaster starts. |
| [track_commit_timestamp](https://www.postgresql.org/docs/16/runtime-config-replication.html#GUC-TRACK-COMMIT-TIMESTAMP) | `on`; this setting is required. | 
| [wal_level](https://www.postgresql.org/docs/16/runtime-config-wal.html#GUC-WAL-LEVEL)      | `logical`; this setting is required by pgEdge. |
| [wal_sender_timeout](https://www.postgresql.org/docs/16/runtime-config-replication.html#GUC-WAL-SENDER-TIMEOUT) | `5s`; this is the minimum value required. |
 
**Note:** On a Multi-master replication system, these parameter settings should be identical on each node.  Additionally, the roles created on each node should be the same.
 

  



