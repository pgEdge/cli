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

my $homedir = "$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $cli = "$ENV{EDGE_CLI}";

print("The home directory is {$homedir}\n");

# First, we call the ./$cli um list command:

my $cmd = qq($homedir/$cli um list);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
print("stdout : @$full_buf \n");

if(!(is_umlist_component_installed($stdout_buf, "$pgversion")))
{
    print("$pgversion not installed. Exiting with code 1\n");
    exit(1);
}


# ERROR CASE: We are misspelling the ./$cli mu list command:

my $cmd1 = qq($homedir/$cli mu list);
print("cmd1 = $cmd1\n");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if(!(contains(@$full_buf1[0], "Invalid")))
{
    exit(1);
}

# We are exercising the .$cli um update command. 

my $cmd2 = qq($homedir/$cli um update);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

if((contains(@$stdout_buf2[0], "Retrieving")))

{
    exit(0);
}
{
    exit(1);
}
