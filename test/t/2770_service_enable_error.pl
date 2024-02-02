# This is a negative test case runs the command:
# ./nodectl service enable pg10
#

use strict;
use warnings;

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


# Checks for service enable providing a component name that is invalid. 

my $cmd = qq($homedir/$cli service enable pg10);
print("cmd = $cmd\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
print("stdout_buf = @$stdout_buf\n");

# Check if the command errored out with the expected message
if (contains(@$stdout_buf[0], "Invalid component parameter"))
 {
    exit(0);
 }
 else
 {
    exit(1);
 }

