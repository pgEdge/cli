# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# ASK CADY: What is an easy way to confirm that the tables have been added to the repsets?





use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1/pgedge";
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2/pgedge";

#
# Then, on each node, invoke spock repset-add-table to add pgbench tables to the repset:
#

my $cmd21 = qq($n1/nodectl spock repset-add-table $repset 'pgbench_*' $database);
print("cmd21 = $cmd21\n");
my($success21, $error_message21, $full_buf21, $stdout_buf21, $stderr_buf21)= IPC::Cmd::run(command => $cmd21, verbose => 0);

print("success21 = $success21\n");
print("stdout_buf21 = @$stdout_buf21\n");

my $cmd22 = qq($n2/nodectl spock repset-add-table $repset 'pgbench_*' $database);
print("cmd22 = $cmd22\n");
my($success22, $error_message22, $full_buf22, $stdout_buf22, $stderr_buf22)= IPC::Cmd::run(command => $cmd22, verbose => 0);

print("success22 = $success22\n");
print("stdout_buf22 = @$stdout_buf22\n");

#
# Test
#

print("If the word 4 is in @$stdout_buf22 we've altered the tables on node 1 to set up pgbench!\n");

my $substring = "ALTER";
if(index($stdout_buf22, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}



