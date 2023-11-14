# In this step, we create the subscription on node 1.

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
our $n3 = "$ENV{EDGE_N3}";


# We can retrieve the home directory for node 1 from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
print("The home directory of node 1 is {$homedir1}\n");

# We can retrieve the port number for node 1 from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $cmd_version`;
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
my $json4 = `$n2/pgedge/nc --json info $cmd_version`;
# print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number of node 2 is {$port2}\n");

print("repuser before chomp = $repuser\n");
chomp($repuser);

print("You'll see a few ERROR statements in the result set for this test script - it tests for missing parameters.");

# Add code to test what happens if a subscription name is omitted:

my $cmd12 = qq($homedir1/nodectl spock sub-create 'host=127.0.0.1 port=$port2 user=$username dbname=$database' $database);
print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
print("stderr_buf12 = @$stderr_buf12\n");

if(!(contains(@$stderr_buf12[0], "ERROR")))
{
    exit(1);
}

# Add code to test what happens if a port number is omitted:

my $cmd13 = qq($homedir1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 user=$username dbname=$database' $database);
print("cmd13 = $cmd13\n");
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
print("stdout_buf13 = @$stdout_buf13\n");

if(!(contains(@$stdout_buf13[0], "failed")))
{
    exit(1);
}

# Add code to test what happens if a user is omitted:

my $cmd14 = qq($homedir1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 port=$port2 user= dbname=$database' $database);
print("cmd14 = $cmd14\n");
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
print("stdout_buf14 = @$stdout_buf14\n");

if(!(contains(@$stdout_buf14[0], "failed")))
{
    exit(1);
}

# Add code to test what happens if a database name is omitted from the connection string:

my $cmd15 = qq($homedir1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 port=$port2 user=$repuser dbname=' $database);
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
print("stdout_buf15 = @$stdout_buf15\n");

if(!(contains(@$stdout_buf15[0], "failed")))
{
    exit(1);
}

# Add code to test what happens if a trailing database name is left off:

my $cmd16 = qq($homedir1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 port=$port2 user=$repuser dbname=$database' );
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);
print("stderr_buf16 = @$stderr_buf16\n");

if(contains(@$full_buf16[0], "ERROR"))

{
    exit(0);
}
else
{
    exit(1);
}

