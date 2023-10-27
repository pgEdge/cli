# You can add more variables to this file as needed, but please be sure you add them to the config.env file as well!

package edge;

our $username = $ENV{EDGE_USERNAME};
our $password = $ENV{EDGE_PASSWORD};
our $database = $ENV{EDGE_DB};
our $inst_version = $ENV{EDGE_INST_VERSION};
our $version = $ENV{EDGE_VERSION};
our $spock = $ENV{EDGE_SPOCK};
our $cluster = $ENV{EDGE_CLUSTER};
our $repset = $ENV{EDGE_REPSET};
our $n1 = $ENV{EDGE_N1};
our $n2 = $ENV{EDGE_N2};
our $n3 = $ENV{EDGE_N3};
our $nodes = $ENV{NODES};

# Leave the 1 on the end of this file:

1;


