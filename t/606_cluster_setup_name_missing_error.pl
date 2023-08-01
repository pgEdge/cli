# This test case creates an installation error.
# ./nodectl cluster create-local demo 2 --pg 18
#
# We also query ./nodectl --json info pg15 to confirm the version of the running instance.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we attempt to create a local cluster with version 18; this will produce an error.
# 

my $cmd = qq(./nodectl cluster create-local 2);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Print statements
#

print("error_message = $error_message\n");
print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

#
print("If the word ERROR is in @$stderr_buf, the test succeeded\n");
#

my $substring = "ERROR";
if (index($stdout_buf, $substring) == -1)

{
  exit(0);
}
else
{
 exit(1);
}

