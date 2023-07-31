# This test case installs hypopg with the commands:
# ./nc um install hypopg-pg16
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";

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
my $json = `./nc --json info`;
print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"homedir"};

print("The home directory is {$homedir}\n"); 

#
# Then, we retrieve the port number from nodectl in json form... this is to catch cases where more than one copy of 
# Postgres is running.
#
my $json2 = `./nc --json info pg16`;
print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};

print("The port number is {$port}\n");

#
# Then, we use the port number from the previous section to connect to psql and test for the existence of the extension.
#

my $cmd5 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -U username -d database -c "SELECT installed_version FROM pg_available_extensions WHERE name='hypopg'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

#
# Test
#

print("success5 = $success5\n");
print("stdout_buf5 = @$full_buf5\n");
print("If there is a version in @$full_buf5 we've installed hypopg!\n");

my $substring = "1";
if(index($stdout_buf5, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}

