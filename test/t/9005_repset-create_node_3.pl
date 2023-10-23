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

my $cmd99 = qq(whoami);
print("cmd99 = $cmd99\n");
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";
my $n3 = "~/work/nodectl/test/pgedge/cluster/demo/n3";

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n3/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n3/pgedge/nc --json info $version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Register node 3 and add the replication set entry on n3: 
print("repuser before chomp = $repuser\n");
chomp($repuser);

my $cmd4 = qq($homedir/nodectl spock node-create n3 'host=127.0.0.1 port=$port user=$repuser dbname=$database' $database);
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

print("We just installed pgedge/spock in $n3.\n");

if(contains(@$stdout_buf5[0], "repset_create"))

{
    exit(0);
}
else
{
    exit(1);
}


