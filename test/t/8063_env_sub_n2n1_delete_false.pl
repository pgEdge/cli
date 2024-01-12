# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this step, we create the subscription on node 2.

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
#increment 1 to the default port for use with node n2
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory of node 2 is $homedir2 \n");

print("The port number of node 2 is $myport2\n");

# Then, create the subscription on node 2:


my $cmd11 = qq($homedir2/$ENV{EDGE_CLI} spock sub-create sub_n2n1 'host=$ENV{EDGE_HOST} port=$ENV{EDGE_START_PORT} user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
print("stdout_buf11 = @$stdout_buf11\n");

 # Adding repset (demo-repset) to the subscripton sub_n1n2

    my $cmd4 = qq($homedir2/$ENV{EDGE_CLI} spock sub-add-repset sub_n2n1 demo-repset $ENV{EDGE_DB});
    print("cmd4 = $cmd4\n");    
    my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

    print("success4 = $success4\n");
    print("stdout_buf4 = @$stdout_buf4\n");

# Then, we connect with psql and confirm that the subscription exists.

my $cmd7 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM spock.subscription");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

# Then, confirm that the subscription exists.

print("We just created the subscription on $ENV{EDGE_CLUSTER_DIR}/n2 and are now verifying it exists.\n");

if(contains(@$stdout_buf7[0], "sub_n2n1"))

{
    exit(0);
}
else
{
    exit(1);
}


