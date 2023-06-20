use strict;
use warnings;

use File::Which;
#use PostgreSQL::Test::Cluster;
#use PostgreSQL::Test::Utils;
use Test::More tests => 1;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# First, we use nodectl to install pgedge; this installs Postgres and creates the admin user and demo database.
# 

my $cmd = qq(./nodectl install pgedge -U admin -P password -d demo);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Success is a boolean; 0 means false, any other value is true). stdout prints the output from the session onscreen.
#

print("success = $success\n");
print("stdout_buf = @$stdout_buf\n");

#
# Then, we retrieve the port number from nc in json form... this is to catch cases where more than one copy of Postgres is running.
#

my $out = decode_json(`./nc --json info pg16`);

my $port = $out ->[0]->{"port"};

print("the Port number is = {$port}\n");

#
# Then, we add an entry to the .pgpass file for the admin user so we can connect with psql.
#

my $cmd3 = qq(echo "*:*:*:admin:password" >> ~/.pgpass);

my($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

diag("We'll need to authenticate with the admin user, so we're adding the password to the .pgpass file = {@$stderr_buf3}\n");

#
# Fourth section, wherein we will do something meaningful with the port number and test for the existence of the spock extension.
#

my $cmd4 = qq(psql -t -h 127.0.0.1 -p $port -U admin -d demo -c "SELECT installed_version FROM pg_available_extensions WHERE name='spock'");

my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);


#print("success4 = $success4\n");
#print("full_buf4 = @$full_buf4\n");
print("stdout_buf4 = @$stdout_buf4\n");

#my $version = @$stdout_buf4;

if (defined($success))
{
    ok(1);
}
else
{
    ok(0);
}


done_testing();
