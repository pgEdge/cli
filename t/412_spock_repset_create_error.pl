# This test case must immediately follow testcases 410 and 411; the set up for this test is in earlier tests.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Create a variable with the path to each node.
# 

my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1";

# Call the command to create a repset, but provide the wronge database name: 
#

my $cmd3 = qq($n1/nodectl spock repset-create my_repset postgres);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("error_message3 = $error_message3\n");
print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");

#
print("If the server reports an ERROR for the missing database name, the test succeeded\n");
#

my $substring = "ERROR";
if (index($stdout_buf3, $substring) == -1)

{
  exit(0);
}
else
{
 exit(1);
}


















