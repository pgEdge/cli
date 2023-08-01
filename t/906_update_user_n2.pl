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

# Then, we connect with psql and update the user on n2.
#

my $cmd9 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6433 -d $database -c "ALTER ROLE $username LOGIN PASSWORD '$password'");
print("cmd9 = $cmd9\n");
my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);

print("success9 = $success9\n");
print("stdout_buf9 = @$stdout_buf9\n");

#
# Test
#

print("stdout_buf9 = @$full_buf9\n");
print("If the word ALTER is in @$full_buf9 we've altered the user and added them to the pgpass file!\n");

my $substring = "ALTER";
if(index($full_buf9, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}

