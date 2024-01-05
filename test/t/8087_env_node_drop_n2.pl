# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll drop the node 2.



use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
# Our parameters are:
#pgedge home directory for n2
my $homedir2="$ENV{EDGE_CLUSTER_DIR}/n2/pgedge";
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory is $homedir2\n"); 

# Drop n2 node

my $cmd2 = qq($homedir2/$ENV{EDGE_CLI} spock node-drop n2 $ENV{EDGE_DB});
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout_buf2 = @$stdout_buf2\n");



if(contains(@$stdout_buf2[0], "node_drop"))

{
    exit(0);
}
else
{
    exit(1);
}

