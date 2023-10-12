# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this step, we drop the subscription on node 2.

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
print("cmd99 = $cmd99\n");
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-nodelete-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory for node 1 from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
print("The home directory of node 1 is {$homedir1}\n");

# We can retrieve the port number for node 1 from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
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
my $json4 = `$n2/pgedge/nc --json info pg16`;
# print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number of node 2 is {$port2}\n");

# Then, drop the subscription on node 2:

print("repuser before chomp = $repuser\n");
chomp($repuser);
my $cmd11 = qq($homedir2/nodectl spock sub-drop sub_n2n1 $database);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
print("stdout_buf11 = @$stdout_buf11\n");

# Then, we connect with psql and confirm that the subscription exists.

my $cmd7 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM spock.subscription");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);


 # Then, use the info to connect to psql and test for the existence of the replication set.
 my $cmd5 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM spock.replication_set WHERE set_name='$repset'");
 print("cmd5 = $cmd5\n");
 my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("stdout_buf5 = @$stdout_buf5\n")

