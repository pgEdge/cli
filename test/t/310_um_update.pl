# This test case runs the command:
# ./nc um update

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


my $homedir = "$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $cli = "$ENV{EDGE_CLI}";

my $cmd2 = qq($homedir/$cli um update);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

if((contains(@$stdout_buf2[0], "Retrieving")))
{
    exit(0);
}
{
    exit(1);
}
