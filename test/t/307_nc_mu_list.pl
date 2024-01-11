# This test case runs the ERROR case: ./nc mu list
#

use strict;
use warnings;

use File::Which;
#use PostgreSQL::Test::Cluster;
#use PostgreSQL::Test::Utils;
#use Test::More tests => 3;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $homedir = "$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $cli = "$ENV{EDGE_CLI}";


my $cmd1 = qq($homedir/$cli mu list);
print("cmd1 = $cmd1\n");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if(!(contains(@$full_buf1[0], "Invalid")))
{
    exit(1);
}

exit(0);