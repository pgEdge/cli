# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this test case, we register node 2 and create the repset on that node.

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

#
# Register node 2 and add the replication set entry on n2: 
#

my $cmd4 = qq($n2/nodectl spock node-create n2 'host=127.0.0.1 port=6433 user=$username dbname=$database' $database);
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("full_buf4 = @$full_buf4\n");
print("stderr_buf4 = @$stderr_buf4\n");
print("We just invoked the ./nc spock node-create n2 command\n");

my $cmd5 = qq($n2/nodectl spock repset-create $repset $database);
print("cmd5 = $cmd5\n");
my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("full_buf5 = @$full_buf5\n");
print("stderr_buf5 = @$stderr_buf5\n");
print("We just created the replication set ($repset\n");

#
# Test
#

print("If the word create is in @$full_buf5 we've just created and registered node 2!\n");

my $substring = "create";
if(index($full_buf5, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}


