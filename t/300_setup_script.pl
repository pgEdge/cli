# This test case runs the command:
# ./nodectl install pgedge --pg 16 -U admin -P password -d demo
# The command does not add an entry to the ~/.pgpass file, so we do that in this case as well, to simplify
# authentication with psql.
# We also query ./nodectl --json info pg16 to find the port number of the running instance in case there is more than 
# one running - the test will use the returned port to log in to psql and confirm that spock has been installed.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we use nodectl to install pgEdge; this installs Postgres and creates the admin user and demo database.
# 

my $cmd = qq(./nodectl install pgedge --pg 16 -U admin -P password -d demo);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Success is a boolean value; 0 means true, any other value is false. 
#
# stdout_buf prints the output from the session onscreen (useful for debugging issues with other modules) if 
# you invoke this file with the perl command - if you invoke it with prove(), the output is suppressed.
#
# print("error_message = $error_message");
print("stdout_buf = @$stdout_buf\n");

#
# Then, we retrieve the port number from nodectl in json form... this is to catch cases where more than one copy of 
# Postgres is running.
#
my $json = `./nc --json info pg16`;
print("my json = $json");
my $out = decode_json($json);

my $port = $out->[0]->{"port"};

print("The port number is = {$port}\n");

#
# Then, we add an entry to the ~/.pgpass file for the admin user so we can connect with psql.
#

my $cmd3 = qq(echo "*:*:*:admin:password" >> ~/.pgpass);
my($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("We'll need to authenticate with the admin user, so we're adding the password to the .pgpass file = {@$stderr_buf3}\n");

#
# We need to get the location of the home directory so we can run psql; store it in $homedir.
#

my $out2 = decode_json(`./nc --json info`);
my $homedir = $out2->[0]->{"home"};
print("the home directory is = {$homedir}\n");

#
# Connect with psql, and confirm that I'm in the correct database.
#

my $cmd5 = qq($homedir/pg16/bin/psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "select * from current_database()");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("success5 = $success5\n");
print("full_buf5 = @$full_buf5\n");
print("stdout_buf5 = @$stdout_buf5\n");

#
# Then, we use the port number from the previous section to connect to psql and test for the existence of the spock extension.
#

my $cmd6 = qq($homedir/pg16/bin/psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "SELECT installed_version FROM pg_available_extensions WHERE name='spock'");
print("cmd6 = $cmd6\n");
my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);

print("success6 = $success6\n");
print("full_buf6 = @$full_buf6\n");
print("stdout_buf6 = @$stdout_buf6\n");

if (defined($success6))
{
    exit(0);
}
else
{
    exit(1);
}
