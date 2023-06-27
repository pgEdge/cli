# This test case runs the commands:
# ./nc list  and ./nc um list and the ERROR case: ./nc mu list
#

use strict;
use warnings;

use File::Which;
#use PostgreSQL::Test::Cluster;
#use PostgreSQL::Test::Utils;
use Test::More tests => 3;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# We are exercising the ./nc list command; a successful run returns 1.
# 

my $cmd = qq(./nc list);
diag("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

diag("success = $success\n");
diag("error_message = $error_message\n");
diag("full_buf = @$full_buf\n");
diag("stdout_buf = @$stdout_buf\n");
diag("stderr_buf = @$stderr_buf\n");

my $version = $success;

if (defined($version))
{
    ok(1);
}
else
{
    ok(0);
}

# 
# We are now exercising the ./nc um list variation; a successful run returns 1.
#

my $cmd2 = qq(./nc um list);
diag("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

diag("success2 = $success2\n");
diag("error_message2 = $error_message2\n");
diag("full_buf2 = @$full_buf2\n");
diag("stdout_buf2 = @$stdout_buf2\n");
diag("stderr_buf2 = @$stderr_buf2\n");

my $version2 = $success2;

if (defined($version2))
{
    ok(1);
}
else
{
    ok(0);
}

#
# We are now exercising the error message for a bad command entry; a successful run returns 0.
#

my $cmd3 = qq(./nc mu list);
diag("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

diag("success3 = $success3\n");
diag("error_message3 = $error_message3\n");
diag("full_buf3 = @$full_buf3\n");
diag("stdout_buf3 = @$stdout_buf3\n");
diag("stderr_buf3 = @$stderr_buf3\n");

my $version3 = $success3;

if (defined($version3))
{
    ok(0);
}
else
{
    ok(1);
}






done_testing();
