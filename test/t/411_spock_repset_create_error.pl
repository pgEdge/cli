# This test case is intended to follow test 410; This test is part of a sequence and 
# the result depends on setup performed in previous scripts: 020, 410, 411, 412, and 414.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2";

#
# Call the command to create a repset, but omit the database name: 
#

my $cmd3 = qq($n1/nodectl spock repset-create my_repset);
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


















