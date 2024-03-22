# In this step, we create the subscription n2n1 on node 2.

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

my $homedir2="$ENV{EDGE_CLUSTER_DIR}/n2/pgedge";
my $n1port = $ENV{'EDGE_START_PORT'};

print("The home directory of node 2 is $homedir2\n");

# Then, create the subscription on node 2:

my $cmd1 = qq($homedir2/$ENV{EDGE_CLI} spock sub-create sub_n2n1 'host=$ENV{EDGE_HOST} port=$n1port user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
print("cmd1 = $cmd1\n");
my $stdout_buf= (run_command_and_exit_iferr ($cmd1))[3];
print("stdout_buf = @$stdout_buf\n");

if(contains(@$stdout_buf, "sub_create"))
{
    print("Subscription created successfully\n");
    exit(0);
}
else
{
    print("Failed to create subscription\n");
    exit(1);
}