# This test case runs the command:
# ./nc service reload pgV
# and then validates the reload.

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
# First, we use nodectl to service reload to pg16; FIXME - add a test for the change to the state of the component.
# 

my $cmd = qq($homedir/$cli service reload $pgversion);
print("cmd = $cmd\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];

if(contains($stdout_buf->[0], "reloading"))
{
    exit(0);
}
else
{
    exit(1);
}
