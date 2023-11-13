# This test case exercises the update manager module.  
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

#
# Move into the pgedge directory

chdir ("./pgedge");

# Node 1:
# We can retrieve the home directory from nodectl in json form...
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $cmd_version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

#
# Move into the pgedge directory

chdir ("./pgedge");

# First, we call the ./nc um list command:

my $cmd = qq($homedir/nc um list);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

if(!(contains(@$stdout_buf[0], "pg")))

{
    exit(1);
}

# ERROR CASE: We are misspelling the ./nc mu list command:

my $cmd1 = qq($homedir/nc mu list);
print("cmd1 = $cmd1\n");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if(!(contains(@$full_buf1[0], "Invalid")))
{
    exit(1);
}

# We are exercising the ./nc um update command. 

my $cmd2 = qq($homedir/nc um update);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

if((contains(@$stdout_buf2[0], "Retrieving")))

{
    exit(0);
}
{
    exit(1);
}
