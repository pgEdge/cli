# In this test case, we confirm that the second node of a two-node cluster is created, and the spock 
# 3.1 extension installed.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

our $username = "$ENV{EDGE_USERNAME}";
our $password = "$ENV{EDGE_PASSWORD}";
our $database = "$ENV{EDGE_DB}";
our $inst_version = "$ENV{EDGE_INST_VERSION}";
our $cmd_version = "$ENV{EDGE_COMPONENT}";
our $spock = "$ENV{EDGE_SPOCK}";
our $cluster = "$ENV{EDGE_CLUSTER}";
our $repset = "$ENV{EDGE_REPSET}";
our $n1 = "$ENV{EDGE_N1}";
our $n2 = "$ENV{EDGE_N2}";

# In this test case, we're just verifying that the second node of a two node cluster has been properly installed 
# by the cluster create-local command.

my $json3 = `$n2/pgedge/nc --json info`;
print("This is from node 2: = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory is {$homedir2}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $cmd_version`;
print("This is also from node 2: = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number is {$port2}\n");

my $cmd30 = qq($homedir2/$cmd_version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM pg_available_extensions WHERE name = 'spock'");
print("cmd30 = $cmd30\n");
my($success30, $error_message30, $full_buf30, $stdout_buf30, $stderr_buf30)= IPC::Cmd::run(command => $cmd30, verbose => 0);
print("stdout_buf on node 2: = @$stdout_buf30\n");

print("If the version is in our search string (@$stdout_buf30) we've confirmed replication is working as expected; if it isn't
        there, this test will fail!\n");

# Test for the search_term in a buffer.

if (contains(@$stdout_buf30[0], "$spock"))

{
    exit(0);
}
else
{
    exit(1);
}
