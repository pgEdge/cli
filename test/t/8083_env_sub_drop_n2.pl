# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this step, we drop the subscription on node 1.

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
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory of node 2 is {$homedir2}\n");

print("The port number of node 2 is {$myport2}\n");

# Then, drop the subscription on node 1:

my $cmd11 = qq($homedir2/nodectl spock sub-drop sub_n2n1 $ENV{EDGE_DB});
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
#print("stdout_buf11 = @$stdout_buf11\n");

# Then, we connect with psql and confirm that the subscription exists.

my $cmd7 = qq($homedir2/$ENV{EDGE_VERSION}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM spock.subscription");
#print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

#print("stdout_buf7=$stdout_buf7\n");

 if(contains(@$stdout_buf11[0], "sub_drop"))

{
    exit(0);
}
else
{
    exit(1);
}
