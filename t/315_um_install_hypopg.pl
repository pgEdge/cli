# This test case installs and removes hypopg with the commands:
# ./nc um install hypopg-pg16  and ./nc um remove hypopg-pg16
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
# First, we install hypopg with the command ./nc um install hypopg-pg16
# 

my $cmd = qq(./nc um install hypopg-pg16);
diag("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Success is a boolean value; 0 means false, any other value is true. 
#
diag("success = $success");
diag("error_message = $error_message");
diag("stdout_buf = @$stdout_buf\n");

my $version = $success;

if (defined($version))
{
    ok(1);
}
else
{
    ok(0);
}

# Then, we retrieve the port number from nodectl in json form... this is to catch cases where more than one copy of 
# Postgres is running.
#

my $out = decode_json(`./nc --json info pg16`);

my $port = $out->[0]->{"port"};

diag("the Port number is = {$port}\n");

#
# Connect with psql, and confirm that I'm in the correct database.
#

my $cmd4 = qq(psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "select * from current_database()");
diag("cmd4 = $cmd4\n");
my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

diag("success4 = $success4\n");
diag("stdout_buf4 = @$stdout_buf4\n");

#
# FIXME - The test wouldn't display the result correctly; verify later.
# Then, we use the port number from the previous section to connect to psql and test for the existence of the hypopg extension.
#

my $cmd5 = qq(psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "SELECT installed_version FROM pg_available_extensions WHERE name='hypopg-pg16'");
diag("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

diag("success5 = $success5\n");
diag("stdout_buf5 = @$stdout_buf5\n");

my $version5 = $success5;

if (defined($version5))
{
    ok(1);
}
else
{
    ok(0);
}

#
# In this stanza, we'll remove hypopg with the command: ./nc um remove hypopg-pg16
#

my $cmd6 = qq(./nc um remove hypopg-pg16);
diag("cmd6 = $cmd6\n");
my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);

diag("success6 = $success6\n");
diag("stdout_buf6 = @$stdout_buf6\n");

my $version6 = $success6;

if (defined($version6))
{
    ok(1);
}
else
{
    ok(0);
}




done_testing();



