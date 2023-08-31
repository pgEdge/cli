# This test case is intended to follow test 410; This test is part of a sequence and 
# the result depends on setup performed in previous scripts: 020, 410, 411, 412, and 414.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Move into the pgedge directory.
#
 chdir("./pgedge/cluster/demo/n1/pgedge/");

# Call the command to create a repset, but omit the database name: 
#

my $cmd3 = qq(./nodectl spock repset-create my_repset);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("error_message3 = $error_message3\n");
if(contains($error_message3, "exited"))

{
    exit(0);
}
else
{
    exit(1);
}



