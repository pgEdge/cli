# This test case runs the command:
# ./nc um list
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
# We are now exercising the ./nc um list variation; a successful run returns 1.
#

my $cmd2 = qq(./nc um list);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("success2 = $success2\n");
print("error_message2 = $error_message2\n");
print("full_buf2 = @$full_buf2\n");
print("stdout_buf2 = @$stdout_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");

my $value = $success2;

if (defined($value))
{
    exit(0);
}
else
{
    exit(1);
}
