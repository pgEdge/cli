# This test case runs the command:
# ./nc service enable pg16
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

# We use nodectl service to enable pg16.
# 

my $cmd = qq(./nc service enable pg16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

# We have a bug in ./nc service enable pg16 - adding this status check to confirm when it's fixed.  For now, this test will fail.

my $cmd2 = qq(./nc service status pg16);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("stdout_buf2 = @$stdout_buf2\n");

if(contains(@$stdout_buf2[0], "start"))

{
    exit(0);
}
else
{
    exit(1);
}


