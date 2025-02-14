# Tutorials

- [Basic Configuration and Usage](tutorials.md#deploying-a-cluster-on-your-localhost)
- [Manually Configuring a Cluster](tutorials.md#manually-configuring-a-cluster)

## Deploying a Cluster on your Localhost

In this tutorial, we'll walk you through the process of creating and modifying a .json file to specify your cluster preferences, and then deploy the cluster with a single command.  This is possibly the simplest way to deploy a cluster for experimentation and test purposes.

### Installing pgEdge Platform

Before starting this tutorial, you should prepare a local host or virtual machine (VM) running EL9 or Ubuntu 22.04. On the host, you should:

* [Set SELinux to `permissive` or `disabled` mode](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux), and reboot the host.
* Configure [passwordless sudo access](../installing_pgedge.mdx#configuring-passwordless-sudo) for a non-root OS user.
* Configure [passwordless ssh](../installing_pgedge.mdx#configuring-passwordless-ssh) access for the same non-root OS user.
* Open any firewalls that could obstruct access between nodes.

Then, install the pgEdge Platform with the command:

`python3 -c "$(curl -fsSL https://pgedge-download.s3.amazonaws.com/REPO/install.py)"`

Paste the command into your command line client and press `Return`.


### Deploying the Cluster

After installing the pgEdge Platform, use the `pgedge localhost cluster-create` command to deploy a cluster (with the `default` replication set and inter-node subscriptions), and create a .json file that describes the cluster configuration. Move into the `pgedge` directory, and invoke the command:

```sql
./pgedge localhost cluster-create cluster_name node_count -d db_name -U db_superuser -P password -port1 port -pg pg_version 
```

When you invoke the command, specify the following values for the positional arguments:

`cluster_name` is the name of the cluster. A directory with this same name will be created in the `cluster` directory; the file describing the cluster configuration will be named `cluster_name.json`.

`node_count` specifies the number of nodes that will be in the cluster.

After providing the values for the positional arguments, provide any optional flags and their corresponding values:

`-d db_name` specifies the name of your PostgreSQL database; the default is `lcdb`.

`-U db_superuser` specifies the username of the database superuser created for this database; the default is `lcusr`.

`-P password` specifies the password of the database superuser.
    
`-port1 port` specifies the port number of the first node created in this cluster; as each subsequent node is created, the port number will increase by `1`.

`-pg pg_version` specifies the PostgreSQL version of the database; choose from versions `15`, `16`, and `17`.

**Example**

```sql
./pgedge localhost cluster-create demo 3 -d lcdb -U lcusr -P 1safepassword -port1 6432 -pg 16  
```

Deploys a cluster described by the `demo.json` file located in the `cluster/demo` directory. The file describes a `3` node cluster with a PostgreSQL `16` database named `lcdb`. The first node of the cluster (`n1`) is listening on port `6432`; `n2` is listening for database connections on `6433` and `n3` is listening for connections on `6434`. The database superuser is named `lcusr`, and the associated password is `1safepassword`.


### Starting Replication on the Cluster

For replication to begin, you will need to add tables to the `default` replication set; for our example, we'll use pgbench to add some tables. When you open pgbench or psql, specify the port number and database name to ensure you're working on the correct node.

Before starting, source the PostgreSQL environment variables on each node to add pgbench and psql to your OS PATH; for example to source the variables on `n1`, use the command:

```sql
source cluster/demo/n1/pgedge/pg16/pg16.env
```

Then, use pgbench to set up a very simple four-table database. At the OS command line, create the pgbench tables in your database (`db_name`) with the `pgbench` command. You must create the tables on each node in your replication cluster:

```sh
pgbench -i --port port_number db_name
```

Then, connect to each node with the psql client:

```sh
psql --port port_number -d db_name
```

Once connected, alter the numeric columns, making the numeric fields conflict-free delta-apply columns, ensuring that the value replicated is the delta of the committed changes (the old value plus or minus any new value) to a given record.  If your cluster is configured to use Spock extension 4.0 (or later) use the commands:

```sql
ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
```

If you're using an older version of the Spock extension (prior to 4.0), use the commands:

```sql
ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (log_old_value=true);
ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (log_old_value=true);
ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (log_old_value=true);
```

Then, exit psql:

```sql
db_name=# exit
```
 
On the OS command line for each node (for example, in the `pgedge/cluster/demo/n1/pgedge` directory), use the `pgedge spock repset-add-table` command to add the tables to the system-created replication set (named `default`); the command is followed by your database name (`db_name`):

```sql
./pgedge spock repset-add-table default 'pgbench_*' db_name
```

 The fourth table, `pgbench_history`, is excluded from the replication set because it does not have a primary key.


### Checking the Configuration

On the psql command line, check the configuration on each node with the following SQL statements:

```sql
db_name=# SELECT * FROM spock.node;
  node_id  | node_name | location | country | info 
-----------+-----------+----------+---------+------
 193995617 | n3        |          |         | 
 673694252 | n1        |          |         | 
 560818415 | n2        |          |         | 
(3 rows)

```
and:

```sql
db_name=# SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription;
   sub_id   | sub_name |      sub_slot_name       |         sub_replication_sets          
------------+----------+--------------------------+---------------------------------------
 3293941396 | sub_n1n2 | spk_lcdb_n2_sub_n1n2 | {default,default_insert_only,ddl_sql}
 1919895280 | sub_n1n3 | spk_lcdb_n3_sub_n1n3 | {default,default_insert_only,ddl_sql}
(2 rows)

```

The `sub_replication_sets` column shown above displays the system-created replication sets. You can add custom replication sets with the [`spock repset-create`](../pgedge_commands/spock.md) and [`spock sub-add-repset`](../pgedge_commands/spock.md) commands.


### Testing Replication

Now, if you update a row on `n1`, you should see the update to the same row on `n2`.

On `n1`:

```sql
db_name=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler
-----+-----+----------+--------
   1 |   1 |    	0 |
 (1 row)
```

```sql
db_name=# UPDATE pgbench_tellers SET filler = 'test' WHERE tid = 1;
UPDATE 1
```

Check `n2` and `n3`:

```sql
db_name=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler  	 
-----+-----+----------+--------------------------------------------------
   1 |   1 |    	0 | test                               
(1 row)
```

You can also use pgbench to exercise replication; exit psql:

```sql
db_name=# exit
```

Then, run the following command on all nodes at the same time to run pgbench for one minute. 

```sql
pgbench -R 100 -T 60 -n --port=port_number db_name
```

When you connect with psql and check the results on both nodes, you'll see that the sum of the `tbalance` columns match on both `pgbench_tellers` tables. Without the conflict-free delta-apply columns, each conflict would have resulted in accepting the first in, potentially leading to sums that do not match between nodes.
 
`n1`:

```sql
db_name=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -101244
(1 row)
```

`n2`:

```sql
db_name=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -101244
(1 row)
```

`n3`:

```sql
db_name=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -101244
(1 row)
```


  
## Manually Configuring a Cluster

This tutorial will walk you through the process of manually configuring each node in a replication scenario. In our example, we'll walk you through creating a two-node multi-master cluster, and then use pgbench to create some tables and perform some read/write activity on the cluster.

### Installing the pgEdge Platform

Before starting this tutorial, you should prepare two (or more) Linux servers running EL9 or Ubuntu 22.04. On each machine, you should:

* [Set SELinux to `permissive` or `disabled` mode on each host](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux), followed by a system reboot.
* Configure passwordless sudo access for a non-root OS user on each host.
* Configure passwordless ssh access for the same non-root OS user on each host.
* Open any firewalls that could obstruct access between your servers.

Create the CLI in a development environment.

### Configuring a Cluster

The first command we use will be the [`setup`](functions/setup.md) command. In addition to the clauses we'll use for this tutorial, the `setup` command allows you to include optional clauses to specify details such as a port number for the cluster (`--port=port_number`), PostgreSQL version (`--pg_ver=version`), Spock version (`--spock_ver=version`), and autostart preferences (`--autostart=True|False`). The `setup` command installs:

* PostgreSQL (Postgres).
* [spock](https://github.com/pgedge/spock), an extension that provides logical, asynchronous, multi-master replication.
* [snowflake](../advanced/snowflake.md), an extension that provides robust sequences for distributed clusters.
* other extensions that support database management on a distributed cluster.

On each server, move into the `pgedge` directory, and invoke the setup command: 

`./pgedge setup -U db_superuser_name -P db_superuser_password -d db_name`

For example, the following command (invoked by an OS user named `rocky`) installs the pgEdge CLI and creates a PostgreSQL database named `acctg`, with a PostgreSQL database superuser named `admin`, whose password is `1safe_password`:

`./pgedge setup -U admin -P 1safe_password -d acctg`

The `setup` command  creates a PostgreSQL database superuser with the name and password you provide with the command. The database user cannot be the name of an OS superuser, `pgedge`, or any of the [PostgreSQL reserved words](https://www.postgresql.org/docs/15/sql-keywords-appendix.html). In the examples that follow, that user is named `admin`.

The `setup` command also creates a [PostgreSQL replication role](https://www.postgresql.org/docs/16/role-attributes.html) with the same name as the OS user that invokes the `setup` command, and adds the username and the scrambled password to the `./pgpass` file. In our example, that user is named `rocky` (the name of the OS user invoking the command). In the steps that follow, this replication user is provided in the connection strings used between nodes for replication.


### Creating Nodes

After installing the CLI and running [setup](functions/setup.md), we'll use [spock node-create](funtions/spock-node-create.md) to create a *replication node* on each host. A replication node is a named collection of databases, tables, and other artifacts that are replicated via a pgEdge subscription. The syntax is:

`./pgedge spock node-create node_name 'host=IP_address_of_n1 user=replication_user_name dbname=db_name' db_name`

When invoking `pgedge spock node-create`, provide three arguments: 

* a name for the node (in our examples, `n1` and `n2`).
* a single-quoted connection string that specifies the node's IP address (for example, `10.0.0.5|10.0.0.6`), the name of the PostgreSQL replication user (`rocky`), and the database name (`acctg`).
* the last argument repeats the database name (`acctg`).

For example, to create node `n1`:

```sql
./pgedge spock node-create n1 'host=10.0.0.5 user=rocky dbname=acctg' acctg
```

To create node `n2`:

```sql
./pgedge spock node-create n2 'host=10.0.0.6 user=rocky dbname=acctg' acctg
```

**Note:** If you use the node naming convention: n1, n2, etc., the `postgresql.conf` file will be automatically updated to enable Snowflake sequences on your cluster.

### Creating Subscriptions

Next, create the subscriptions that connect the nodes to each other. Since this is a multi-master replication system, each node acts as both a subscriber and a publisher node. Use the command:

```sql
./pgedge spock sub-create subscription_name 'host=IP_address_of_publisher port=port_number user=replication_user_name dbname=db_name' db_name
```

When invoking the command, provide three arguments: 

* a unique subscription name for each node (in the examples that follow, `sub_n1n2` and `sub_n2n1`).
* a single-quoted connection string that specifies the IP address of the node you're subscribing to (in our examples, `10.0.0.5` and `10.0.0.6`), the PostgreSQL port on the publisher node (`5432`), the name of the PostgreSQL replication user (`rocky`), and the database name (`acctg`).
* the last argument repeats the database name (`acctg`).

For example, if  you have a two node cluster, you'll create two subscriptions; one that subscribes node 1 to node 2 and one that subscribes node 2 to node 1:

On node `n1`:

```sql
./pgedge spock sub-create sub_n1n2 'host=10.0.0.6 port=5432 user=rocky dbname=acctg' acctg
```

On node `n2`:

```sql
./pgedge spock sub-create sub_n2n1 'host=10.0.0.5 port=5432 user=rocky dbname=acctg' acctg
```


### Adding Tables to the Replication Set

For replication to begin, you will need to add tables to the replication set; for this example, we'll use pgbench to add some tables. When you open pgbench or psql, specify your database name after the utility name.

On each node, source the PostgreSQL environment variables to add pgbench and psql to your OS PATH; this will make it easier to move between the nodes:

```sql
source pg16/pg16.env
```

Then, use pgbench to set up a very simple four-table database. At the OS command line, (on each node of your replication set), create the pgbench tables in your database (`db_name`) with the `pgbench` command. You must create the tables on each node in your replication cluster:

```sql
pgbench -i db_name
```

Then, connect to each node with the psql client:

```sql
psql db_name
```

Once connected, alter the numeric columns, making the numeric fields conflict-free delta-apply columns, ensuring that the value replicated is the delta of the committed changes (the old value plus or minus any new value) to a given record. Use the commands:

```sql
ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (log_old_value=true, delta_apply_function=spock.delta_apply);
```

Then, exit psql:

```sql
db_name=# exit
```
 
On the OS command line for each node, use the `pgedge spock repset-add-table` command to add the tables to the system-created replication set (named `default`); the command is followed by your database name (`db_name`):

```sql
./pgedge spock repset-add-table default 'pgbench_*' db_name
```

 The fourth table, `pgbench_history`, is excluded from the replication set because it does not have a primary key.


### Checking the Configuration

On the psql command line, check the configuration on each node with the following SQL statements:

```sql
psql db_name

db_name=# SELECT * FROM spock.node;
node_id | node_name
---------+----------
673694252 | n1
560818415 | n2
(2 rows)
```
and:

```sql
db_name=# SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription;
   sub_id   | sub_name |	sub_slot_name 	|                	sub_replication_sets             
------------+----------+----------------------+--------------------------------------------------------
 3293941396 | sub_n1n2 | spk_db_name_n2_sub_n1n2 | {default,default_insert_only,ddl_sql}
(1 row)
```

The `sub_replication_sets` column shown above displays the system-created replication sets. You can add custom replication sets with the [`spock repset-create`](../pgedge_commands/spock.md) and [`spock sub-add-repset`](../pgedge_commands/spock.md) commands.


### Testing Replication

Now, if you update a row on `n1`, you should see the update to the same row on `n2`.

On `n1`:

```sql
db_name=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler
-----+-----+----------+--------
   1 |   1 |    	0 |
 (1 row)
```

```sql
db_name=# UPDATE pgbench_tellers SET filler = 'test' WHERE tid = 1;
UPDATE 1
```

Check `n2`:

```sql
db_name=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler  	 
-----+-----+----------+--------------------------------------------------
   1 |   1 |    	0 | test                               
(1 row)
```

You can also use pgbench to exercise replication; exit psql:

```sql
db_name=# exit
```

Then, run the following command on both nodes at the same time to run pgbench for one minute. 

```sql
pgbench -R 100 -T 60 -n db_name
```

When you connect with psql and check the results on both nodes, you'll see that the sum of the `tbalance` columns match on both `pgbench_tellers` tables. Without the conflict-free delta-apply columns, each conflict would have resulted in accepting the first in, potentially leading to sums that do not match between nodes.
 
`n1`:

```sql
db_name=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -84803
(1 row)
```

`n2`:

```sql
db_name=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -84803
(1 row)
```


