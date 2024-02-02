
# This test case runs the command:
# ./nc service start pgV
# and performs the necessary validation before and after.

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $homedir = "$ENV{EDGE_HOME_DIR}";
my $cli = $ENV{EDGE_CLI};
my $pgversion = $ENV{EDGE_COMPONENT};
my $exitcode = 0;
#
# We use nodectl to service start pg16.
# 

# Checking service status
my $cmd0 = qq($homedir/$cli service status $pgversion);
print("cmd = $cmd0\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd0))[3];
print("stdout_buf : @$stdout_buf");

# If server is stopped, we attempt to service start it
if (contains(@$stdout_buf[0], "stopped on port"))
 {
    # service start pgV
    my $cmd = qq($homedir/$cli service start $pgversion);
    print("cmd = $cmd\n");
    my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
    print("stdout_buf : @$stdout_buf");
    # if service start was successful 
    if(contains(@$stdout_buf[0], "starting on port"))
    {
        print("$pgversion started successfully. Exiting with success\n");
        $exitcode = 0;
    }
    else
    {
        $exitcode = 1;
    }
}
else 
{
    print("$pgversion already running. Exiting with failure\n");
    $exitcode = 1;
}

exit ($exitcode);
