# This test case runs the command:
# ./nc service restart pgV
#

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

#
# We use nodectl to service restart pg16.
# 

my $cmd = qq($homedir/$cli service restart $pgversion);
print("cmd = $cmd\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
print("stdout_buf : @$stdout_buf");

# A successfull restart returns two lines, stopping pgV in its line 0 and starting pgV in its line 1
if(contains(@$stdout_buf[0], "stopping") && contains(@$stdout_buf[1], "starting"))
{
    exit(0);
}
else
{
    exit(1);
}

