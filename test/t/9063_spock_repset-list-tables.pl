# Test spock repset-list-tables
# 

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
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory for node 1 from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
#print("The home directory of node 1 is {$homedir1}\n");

# We can retrieve the port number for node 1 from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port1 = $out2->[0]->{"port"};
#print("The port number on node 1 is {$port1}\n");


# We can retrieve the home directory for node 2 from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
#print("The home directory of node 2 is {$homedir2}\n");

# We can retrieve the port number for node 2 from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info pg16`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
#print("The port number of node 2 is {$port2}\n");


# Add code to test what happens if a schema name is omitted; this should throw an ERROR:

my $cmd15 = qq($homedir1/nodectl spock repset-list-tables $database);
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);

if(!(contains(@$full_buf15[0], "ERROR")))
{
    exit(1);
}

# Add code to test what happens if the schema name and database name are omitted; this should throw an ERROR:

my $cmd16 = qq($homedir1/nodectl spock repset-list-tables);
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);

if(!(contains(@$full_buf16[0], "ERROR")))
{
    exit(1);
}

# Calling the command properly returns a set of tables in demo-repset:

my $cmd10 = qq($homedir2/nodectl spock repset-list-tables public $database);
print("cmd10 = $cmd10\n");
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);

if(contains(@$stdout_buf10[0], "demo-repset"))

{
    exit(0);
}
else
{
    exit(1);
}


