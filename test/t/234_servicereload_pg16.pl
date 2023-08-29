# This test case runs the command:
# ./nc service reload pg16
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we use nodectl to service reload to pg16; FIXME - add a test for the change to the state of the component.
# 

my $cmd = qq(./nc service reload pg16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");

if(contains(@$stdout_buf[0], "reloading"))

{
    exit(0);
}
else
{
    exit(1);
}


