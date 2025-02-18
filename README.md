# The Command Line Interface (CLI)

## Table of Contents
- [Creating a Development Environment](README.md#creating-a-development-environment)
- [CLI Functions](docs/cli_functions.md)
- [Tutorials](docs/tutorials.md)
- [Release Notes](docs/cli_release_notes.md)

This is the Command Line Interface (CLI) for managing components. 

### Creating a Development Environment

1.) Clone this repository.

2.) Move into the setup directory: `cd cli/devel/setup`

3.) Run the setup scripts: `./10-toolset.sh` through `30-bashrc.sh`

4.) Source the `~/.bashrc` file.

5.) Run `40-awscli.sh` to install AWS in a virtual environment.

6.) Configure your `~/.aws/config` credentials.

7.) Run `50-pull-IN.sh` to retrieve the REPO files.

### Using the CLI

On each machine that will host a replication node, you must:

* Open any firewalls that could obstruct access between your servers.
* [Set SELinux to `permissive` or `disabled` mode on each host](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux), followed by a system reboot.
* Configure [passwordless sudo access](#configuring-passwordless-sudo) for a non-root OS user on each host.
* Configure [passwordless ssh](#configuring-passwordless-ssh) access for the same non-root OS user on each host.

There are a number of considerations that should go into your [schema design](https://docs.pgedge.com/platform/prerequisites/configuring) to really take advantage of pgEdge active-active replication.

#### Configuring Passwordless SSH

You can use the following steps to configure passwordless SSH on each node of the replication cluster:

```sh
ssh-keygen -t rsa
cd ~/.ssh
cat id_rsa.pub >> authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

#### Configuring Passwordless sudo

To configure passwordless sudo, open the /etc/sudoers file, and add a line of the form:

%username         ALL = (ALL) NOPASSWD: ALL

Where `username` specifies the name of your operating system user.

#### Considerations

When designing a schema for use with the CLI, you should ensure that you:

**Include a Primary Key in Each Table** 

All tables must include a primary key; this allows pgEdge to replicate `INSERT`, `UPDATE`, and `DELETE` statements. If your table does not include a primary key, only `INSERT` statements will be replicated to the table.

**Use Snowflake Sequences instead of PostgreSQL sequences** 

If you use a PostgreSQL sequence as part of your primary key, you should convert your sequences to [Snowflake sequences](https://github.com/pgEdge/snowflake). Snowflake sequences are composed of multiple data types that ensure a unique transaction sequence when processing your data in multiple regions. This helps  accurately preserve the order in which globally distributed transactions are performed, and alleviates concerns that network lag could disrupt sequences in distributed transactions.

**Include the ENABLE ALWAYS clause in Triggers** 

PostgreSQL triggers will fire only from the node on which they were invoked. If you have triggers that are related to the replication process, you should include the `ENABLE ALWAYS` clause when attaching a trigger to a table:

```
CREATE TRIGGER ins_trig AFTER INSERT ON my_table FOR EACH ROW EXECUTE PROCEDURE ins_history();
ALTER TABLE trans_history ENABLE ALWAYS TRIGGER ins_trig;
```
