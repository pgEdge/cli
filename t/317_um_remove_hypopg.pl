# This test case removes hypopg with the command:
# ./nc um remove hypopg-pg16
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
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# In this stanza, we'll remove hypopg with the command: ./nc um remove hypopg-pg16
#

my $cmd = qq(./nc um remove hypopg-pg16);
print("cmd = $cmd\n");
my($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("success = $success\n");
print("error_message = $error_message\n");
print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

my $value = $success;

if (defined($value))
{
    exit(0);
}
else
{
    exit(1);
}

