# This test case runs the ERROR case: ./nc mu list
#

use strict;
use warnings;

use File::Which;
#use PostgreSQL::Test::Cluster;
#use PostgreSQL::Test::Utils;
#use Test::More tests => 3;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;


#
# Move into the pgedge directory
#

chdir ("./pgedge");

#
# We are now exercising the error message for a bad command entry; a successful run returns 0.
#

my $cmd3 = qq(./nc mu list);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("success3 = $success3\n");
print("error_message3 = $error_message3\n");
print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");

if (defined($error_message3))
{
    exit(0);
}
else
{
    exit(1);
}
