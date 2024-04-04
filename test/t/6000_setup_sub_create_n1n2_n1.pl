# In this step, we create the subscription n1n2 on node 1.

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

my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $n2port = $ENV{'EDGE_START_PORT'} + 1;

print("The home directory of node 1 is $homedir1\n");

# Then, create the subscription on node 1:

my $cmd1 = qq($homedir1/$ENV{EDGE_CLI} spock sub-create sub_n1n2 'host=$ENV{EDGE_HOST} port=$n2port user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
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