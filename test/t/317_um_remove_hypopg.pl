# This test case removes hypopg with the command:
# ./nc um remove hypopg-pg16
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

my $port = $ENV{EDGE_START_PORT};
my $pgversion = $ENV{EDGE_COMPONENT};
my $homedir="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $cli = $ENV{EDGE_CLI};
my $component = "hypopg-$pgversion";
my $exitcode = 1;

my $cmd = qq($homedir/$cli um remove $component);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("success = $success\n");
print("stdout_buf = @$stdout_buf\n");

my $cmd2 = qq($homedir/$cli um list);
print("cmd = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success2)) 
{
    if (is_umlist_component_installed($stdout_buf2, $component)) {
        print("$component is still Installed. Failure\n");
        $exitcode = 1;
    } else {
        print("$component uninstalled successfully\n");
        $exitcode = 0;
    }
} 
else
{
    print("$cmd2 not executed successfully. full buffer :  @$full_buf\n");
    $exitcode = 1;
} 

exit($exitcode);
