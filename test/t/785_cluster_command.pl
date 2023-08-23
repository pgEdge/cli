# This test case demonstrates that the command can be used to invoke a command on any node in a 
# cluster.  The command tested is:
# ./nodectl cluster command demo n2 "info pg16 --json"
#
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



my $cmd = qq(./nodectl cluster command demo n2 "info pg16 --json");
print("cmd = $cmd\n");
my($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("success = $success\n");
print("stdout_buf = @$stdout_buf\n");

if (defined($success))

{
  exit(0);
}
else
{
 exit(1);
}

