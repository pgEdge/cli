# You can add more variables to this file as needed, but please be sure you add them to the config.env file as well!

package edge;

our $username = $ENV{EDGE_USERNAME};
our $password = $ENV{EDGE_PASSWORD};
our $database = $ENV{EDGE_DBNAME};
our $inst_version = $ENV{EDGE_INST_VERSION};
our $version = $ENV{EDGE_CMD_VERSION};
our $spock = $ENV{EDGE_SPOCK_VERSION};
our $cluster = $ENV{EDGE_CLUSTER_NAME};
our $repset = $ENV{EDGE_REPSET_NAME};
our $n1 = $ENV{EDGE_PATH_TO_N1};
our $n2 = $ENV{EDGE_PATH_TO_N2};
our $n3 = $ENV{EDGE_PATH_TO_N3};


# Leave the 1 on the end of this file:

1;


