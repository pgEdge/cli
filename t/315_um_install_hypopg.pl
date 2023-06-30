# This test case installs hypopg with the commands:
# ./nc um install hypopg-pg16
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
# First, we install hypopg with the command ./nc um install hypopg-pg16
# 

my $cmd = qq(./nc um install hypopg-pg16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Success is a boolean value; 0 means true, any other value is false. 
#
print("success = $success");
print("error_message = $error_message");
print("stdout_buf = @$stdout_buf\n");

my $value = $success;

#
# Then, we retrieve the port number from nodectl in json form... this is to catch cases where more than one copy of 
# Postgres is running.
#
my $json = `./nc --json info pg16`;
print("my json = $json");
my $out = decode_json($json);

my $port = $out->[0]->{"port"};
print("The port number is {$port}\n");
#
# Connect with psql, and confirm that I'm in the correct database.
#

my $cmd4 = qq(psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "select * from current_database()");
print("cmd4 = $cmd4\n");
my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("success4 = $success4\n");
print("stdout_buf4 = @$stdout_buf4\n");

#
# Then, we use the port number from the previous section to connect to psql and test for the existence of the extension.
#

my $cmd5 = qq(psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "SELECT installed_version FROM pg_available_extensions WHERE name='hypopg'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

if (defined($success5))
{
    exit(0);
}
else
{
    exit(1);
}

