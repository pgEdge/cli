# ACE (Anti-Chaos Engine)

ACE is a powerful tool designed to ensure and maintain consistency across nodes in a replication cluster managed by the [Spock extension](https://github.com/pgEdge/spock). It helps identify and resolve data inconsistencies, schema differences, and replication configuration mismatches across nodes in a cluster.

## Table of Contents
- [Building the ACE Extension](README.md#building-the-ace-extension)
- [Managing Data Consistency with ACE](docs/ace_overview.md)
- [Using ACE Functions](docs/ace_functions.md)
- [ACE API Endpoints](docs/ace_api.md)
- [Scheduling ACE Operations](docs/ace_schedule.md)

<<<<<<< HEAD
ACE is installed with the pgEdge Platform installer. The following commands describe installing ACE on a management system that is not a member of a replication cluster:
=======
### Building the ACE Extension

ACE is installed by the CLI installer. The following commands describe installing ACE on a management system (that is not a member of a replication cluster):
>>>>>>> 14ff79fb (Adding OS docs folder with expanded docs and README file for ACE with TOC to access content in docs folder.)

1. After installing the [CLI](https://github.com/pgEdge/cli), navigate to the directory where ACE will be installed.

2. Invoke the CLI [UM installer](https://github.com/pgEdge/cli/blob/REL25_01/docs/functions/um-install.md) in that location with the command: 

`pgedge um install ace`

3. Create a directory named `cluster` in the `pgedge` directory. 

4. [Create and update a .json file](https://github.com/pgEdge/cli/blob/REL25_01/docs/functions/cluster-json-template.md), and place the file in `cluster/cluster_name/cluster_name.json` on the ACE host.  For example, if your cluster name is `us_eu_backend`, the cluster definition file for this should be placed in `/pgedge/cluster/us_eu_backend/us_eu_backend.json`.  The .json file must: 

<<<<<<< HEAD
=======
    * Contain connection information for each node in the cluster in the node's stanza.
    * Identify the user that will be invoking ACE commands in the `db_user` property.  This user must also be the table owner.
    
After ensuring that the .json file describes your cluster connections and identifies the ACE user, you're ready to use [ACE commands](docs/ace_functions.md).
>>>>>>> 14ff79fb (Adding OS docs folder with expanded docs and README file for ACE with TOC to access content in docs folder.)

### The Cluster JSON File

ACE uses the cluster definition JSON file to connect to nodes and execute SQL statements. It might even be desirable to set up a connection pooler like pgBouncer or pgCat separately and point to that in the cluster JSON file for faster runtime performance.