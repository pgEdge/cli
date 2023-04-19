# pgEdge Platform - Getting Started Guide

In this guide we will step through setting up pgEdge Platform. We’ll focus for now on setting this up on Rocky Linux 8, however very similar steps are used on Debian based systems or on MacOS. Our goal in this guide is to create a multi-active pgEdge cluster and then use pgbench to create some representative tables and read/write activity on the cluster.

Two software components from pgEdge will be used in this guide. First, we’ll install `nodectl` which is used to configure Postgres and install additional extensions. Second is `Spock`, the Postgres extension providing *logical, multi-active replication*.

You’ll need root permissions on these systems in order to install any OS packages needed as prerequisites.

## Prerequisites
- Enterprise Linux (EL) 8/9, Ubuntu 20.04/22.04, Debian 11, OSX M1/M2
- A non-root user with `sudo` privileges
- `systemctl` available
- `Python 3.8+`& an updated `pip3` to install packages as per below
- Two servers (vm's are fine) networked with traffic on port 5432 allowed
- SSH access into the servers

On EL8 systems, upgrade to Python 3.9 (from default Python 3.6) as follows:
<pre>
sudo yum install python39 python39-devel; sudo yum remove python3
</pre>

Get the latest 23.x version of PIP3 installed:
<pre>
curl -O  https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
</pre>

On Ubuntu you'll want to add ~/.local/bin to your path so latest PIP3 will be picked up.

Use PIP3 to install CLI dependencies as follows:
<pre>
pip3 install psycopg psycopg-binary psutil paramiko --user
</pre>

## Installation
In any directory owned by your user, use the following command to install `nodectl`:
<pre>
python3 -c "$(curl -fsSL https://pgedge-upstream.s3.amazonaws.com/REPO/install.py)"
</pre>

cd into the `pgedge` directory created and install the ***pgEdge Platform*** with the `nc` command. Specify a superuser name, password, and a database name. Note that the names cannot be pgEdge and cannot be any postgreSQL reserved words. For the examples given in this documentation, I will be using a database named demo.
<pre>
./nodectl spock install -U superuser-name -P superuser-password -d database-name
</pre>

For this demo I will be using the following command:
<pre>
./nodectl spock install -U admin -P mypassword1 -d demo
</pre>


If you encounter an error running this command, you may need to update your SELINUX mode to permissive, reboot, and retry the operation.

## Configuration 
Using nodectl on each node, create the spock components needed for replication. First you will create a spock node by providing the name of the node, network address, and database name. You will provide the IP address of each node and the name of the pgedge user which has been created for replication, not the super user you created. Next you will make replication sets by providing the replication set name and the database name. For both the node name (n1) and the replication set name (demo_replication_set), these can be whatever you want but you will have to reference them in future commands.

Node `n1` (IP address 10.1.2.5):
<pre>
./nodectl spock node-create n1 'host=10.1.2.5 user=pgedge dbname=demo' demo
./nodectl spock repset-create demo_replication_set demo
</pre>

Node `n2` (IP address 10.2.2.5):
<pre>
./nodectl spock node-create n2 'host=10.2.2.5 user=pgedge dbname=demo' demo
./nodectl spock repset-create demo_replication_set demo
</pre>

Next, use nodectl to create the subscriptions. For these commands you will provide the subscription name, the network address for the node this one is subscribing to, and the database name.

Node `n1`:
<pre>
./nodectl spock sub-create sub_n1n2 'host=10.2.2.5 port=5432 user=pgedge dbname=demo' demo
</pre>

Node `n2`:
<pre>
./nodectl spock sub-create sub_n2n1 'host=10.1.2.5 port=5432 user=pgedge dbname=demo' demo
</pre>

At this point, you will have a two node cluster with cross subscriptions on `n1` to `n2` and `n2` to `n1`. For replication to begin, you will need to add tables to the replication sets and then add those replications to the subscriptions. For this demo, I will be using pgBench to set up a very simple four table database.

You can source the postgres environment variables and connect to your database with:
<pre>
source pg15/pg15.env
</pre>

This also adds pgbench and psql to your PATH. When using either command, you will still need to specify your database name, for example:
<pre>
psql demo
</pre>

Initialize with the pgBench command, psql into the postgreSQL database:
<pre>
pgbench -i demo
</pre>
 
Once connected to the database, alter the numeric columns to have `LOG_OLD_VALUE` equal to true.  This will make these numeric fields Conflict-Free Delta-Apply columns.
<pre>
ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true);
ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true);
ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true);
</pre>

Dump and restore the database on to node 2 so that you are left with two databases with the same schema and data.<br> 

`n1`:
<pre>
pg_dump -v -d demo > dump-1.sql
</pre>

Copy file to `n2`, and run on `n2`:
<pre>
psql demo -f dump-1.sql
</pre>

Run the following on both nodes to add these tables to the replication set. The fourth table, pgbench_history, cannot be added because it does not have a primary key.
<pre>
./nodectl spock repset-add-table demo_replication_set pgbench_branches demo
./nodectl spock repset-add-table demo_replication_set pgbench_tellers demo
./nodectl spock repset-add-table demo_replication_set pgbench_accounts demo
</pre>

Finish the set up by adding the replication sets to the subscriptions you had created.<br>
`n1`:
<pre>
./nodectl spock sub-add-repset sub_n1n2 demo_replication_set demo
</pre>

`n2`:
<pre>
./nodectl spock sub-add-repset sub_n2n1 demo_replication_set demo
</pre>

Check the configuration with the following sql statements
<pre>
demo=# SELECT * FROM spock.node;
node_id | node_name
---------+----------
673694252 | n1
560818415 | n2
(2 rows)
</pre>
<pre>
demo=# SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription;
   sub_id   | sub_name |	sub_slot_name 	|                	sub_replication_sets             
------------+----------+----------------------+--------------------------------------------------------
 3293941396 | sub_n1n2 | spk_demo_n2_sub_n1n2 | {default,default_insert_only,ddl_sql,demo_replication_set}
(1 row)
</pre>
## Test Replication
Run an update on `n1` to see the update on `n2`.

`n1`:
<pre>
demo=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler
-----+-----+----------+--------
   1 |   1 |    	0 |
 (1 row)
</pre>

<pre>
demo=# UPDATE pgbench_tellers SET filler = 'test' WHERE tid = 1;
UPDATE 1
</pre>

Check `n2`:
<pre>
demo=# SELECT * FROM pgbench_tellers WHERE tid = 1;
 tid | bid | tbalance | filler  	 
-----+-----+----------+--------------------------------------------------
   1 |   1 |    	0 | test                               
(1 row)
</pre>

Run the following command on both nodes at the same time to run pgBench for one minute. 
<pre>
pgbench -R 100 -T 60 -n demo
</pre>

Check the results on both nodes and see that the sum of the tbalance columns match on both pgbench_tellers tables. Without the Conflict-Free Delta-Apply columns, each conflict would have resulted in accepting the first in, potentially leading to sums that do not match between nodes.
 
`n1`:
<pre>
demo=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -84803
(1 row)
</pre>

`n2`:
<pre>
demo=# SELECT SUM(tbalance) FROM pgbench_tellers;
  sum  |
 ------+
 -84803
(1 row)
</pre>


