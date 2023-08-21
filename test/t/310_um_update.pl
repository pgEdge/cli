# This test case runs the command:
# ./nc um update

use strict;
use warnings;

use File::Which;
#use PostgreSQL::Test::Cluster;
#use PostgreSQL::Test::Utils;
#use Test::More tests => 1;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we find the list of available components with ./nc um update
# 

my $cmd = qq(./nc um update);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("stdout_buf = @$stdout_buf\n");

my $version = $success;

if (defined($version))
{
    exit(0);
}
else
{
    exit(1);
}
