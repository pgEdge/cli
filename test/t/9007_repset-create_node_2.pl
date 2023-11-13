# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this test case, we register node 2 and create the repset on that node.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

our $repuser = `whoami`;
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

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n2/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n2/pgedge/nc --json info $ENV{EDGE_COMPONENT}`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Register node 2 and add the replication set entry on n2: 
print("repuser before chomp = $repuser\n");
chomp($repuser);

my $cmd4 = qq($homedir/nodectl spock node-create n2 'host=127.0.0.1 port=$port user=$repuser dbname=$database' $database);
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("stdout_buf4 = @$stdout_buf4\n");
print("We just invoked the ./nc spock node-create n2 command\n");

my $cmd5 = qq($homedir/nodectl spock repset-create $repset $database);
print("cmd5 = $cmd5\n");
my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("stdout_buf5 = @$stdout_buf5\n");
print("We just executed the command that creates the replication set (demo-repset)\n");

# Test to confirm that cluster is set up.

print("We just installed pgedge/spock in $n1.\n");

if(contains(@$stdout_buf5[0], "repset_create"))

{
    exit(0);
}
else
{
    exit(1);
}


