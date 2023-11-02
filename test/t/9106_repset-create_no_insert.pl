# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.
# After creating the repset, we'll query the spock.replication_set_table to see if the repset exists. 


use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './lib';
use contains;

# Our parameters are:

my $cmd99 = qq(whoami);
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


# We can retrieve the home directory for node 1 from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
print("The home directory of node 1 is {$homedir1}\n");

# We can retrieve the port number for node 1 from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $version`;
# print("my json = $json2");
my $out2 = decode_json($json2);
my $port1 = $out2->[0]->{"port"};
print("The port number on node 1 is {$port1}\n");


# We can retrieve the home directory for node 2 from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
# print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory of node 2 is {$homedir2}\n");

# We can retrieve the port number for node 2 from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
# print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number of node 2 is {$port2}\n");


# Register node 1 and the repset on n1: 
print("repuser before chomp = $repuser\n");
chomp($repuser);
my $cmd2 = qq($homedir1/nodectl spock node-create n1 'host=127.0.0.1 port=$port1 user=$repuser dbname=$database' $database);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("stdout_buf2 = @$stdout_buf2\n");

my $cmd3 = qq($homedir1/nodectl spock repset-create --replicate_insert=False $repset $database);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
print("stdout_buf3 = @$stdout_buf3\n");

print("We just executed the command that creates the replication set (demo-repset) on $n1\n");


# Register node 2 and add the replication set entry on n2: 
print("repuser before chomp = $repuser\n");
chomp($repuser);

my $cmd4 = qq($homedir2/nodectl spock node-create n2 'host=127.0.0.1 port=$port2 user=$repuser dbname=$database' $database);
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("stdout_buf4 = @$stdout_buf4\n");
print("We just invoked the ./nc spock node-create n2 command\n");

my $cmd5 = qq($homedir2/nodectl spock repset-create --replicate_insert=False $repset $database);
print("cmd5 = $cmd5\n");
my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("stdout_buf5 = @$stdout_buf5\n");
print("We just executed the command that creates the replication set (demo-repset)\n");


# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd15 = qq($homedir1/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM spock.replication_set");
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
print("stdout_buf15 = @$stdout_buf15\n");
# Test to confirm that cluster is set up.

if(contains(@$stdout_buf15[0], "demo-repset"))

{
    exit(0);
}
else
{
    exit(1);
}





