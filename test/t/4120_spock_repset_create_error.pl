# This test case must immediately follow testcases 410 and 411; the set up for this test is in earlier tests.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


# Call the command to create a repset, but provide the wrong database name: 

my $cmd3 = qq(./nodectl spock repset-create my_repset postgres);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("error_message3 = $error_message3\n");
print("stdout_buf3 = @$stdout_buf3\n");


print("If the server reports an ERROR for the wrong database name, the test succeeded\n");

if(contains($error_message3, "failed"))
{
    exit(0);
}
else
{
    exit(1);
}

