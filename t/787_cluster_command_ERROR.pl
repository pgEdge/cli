# This test case demonstrates that the following command will gracefully return an ERROR if invoked on a
# cluster that does not exist. 
# The command tested is:
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

my $cmd = qq(./nodectl cluster command demo no_n2 "info pg16 --json");
print("cmd = $cmd\n");
my($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("If the content of my substring is in @$stderr_buf, the test succeeded\n");

my $substring = "cluster/demo/no_n2/nodectl";

if (index($stdout_buf, $substring) == -1)

{
  exit(0);
}
else
{
 exit(1);
}


