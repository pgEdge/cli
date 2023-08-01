# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
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
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1/pgedge";
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2/pgedge";


# Then, we add an entry to the ~/.pgpass file for the user.
#

my $cmd10 = qq(echo "*:*:*:$username:$password" >> ~/.pgpass);
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);

print("$cmd10 adds the password to the pgpass file.\n");


#
# Then, we connect with psql and confirm that the user exists and has a password.
#

my $cmd7 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "ALTER ROLE $username LOGIN PASSWORD '$password'");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

print("success7 = $success7\n");
print("stdout_buf7 = @$stdout_buf7\n");

#
# Test
#

print("success7 = $success7\n");
print("full_buf7 = @$full_buf7\n");
print("If the word ALTER is in @$full_buf7 we've altered the user entry with psql!\n");

my $substring = "ALTER";
if(index($stdout_buf7, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}

