# Test spock sub-show-table
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
my $version = "pg17";
my $spock = "3.2";
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
my $json2 = `$n1/pgedge/nc --json info $version`;
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
my $json4 = `$n2/pgedge/nc --json info $version`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
#print("The port number of node 2 is {$port2}\n");

print("This script tests what happens if parameters are omitted, so the log file should contain ERROR statements here.\n");

# Confirm that spock sub-show-tables errors-out gracefully if the subscription name is missing:

my $cmd10 = qq($homedir2/nodectl spock sub-show-table pgbench_accounts lcdb);
print("cmd10 = $cmd10\n");
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);

if(!(contains(@$stderr_buf10[0], "ERROR")))
{
    exit(1);
}

# Confirm that spock sub-show-status errors-out gracefully if the database name is missing:

my $cmd11 = qq($homedir2/nodectl spock sub-show-table sub_n2n1 pgbench_accounts);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);

if(!(contains(@$stderr_buf11[0], "ERROR")))
{
    exit(1);
}

# Confirm that spock sub-show-status errors-out gracefully if the table name is missing:

my $cmd12 = qq($homedir2/nodectl spock sub-show-table sub_n2n1 lcdb);
print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);

if(!(contains(@$stderr_buf12[0], "ERROR")))
{
    exit(1);
}

# Use spock sub-show-status to check the status of sub_n2n1:

my $cmd13 = qq($homedir2/nodectl spock sub-show-table sub_n2n1 pgbench_accounts lcdb);
print("cmd13 = $cmd13\n");
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
print("stdout_buf13 = @$stdout_buf13\n");

if(contains(@$stdout_buf13[0], "pgbench_accounts"))

{
    exit(0);
}
else
{
    exit(1);
}


