# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.

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
# Register node 1 and the repset entry on n1: 
#

my $cmd2 = qq($n1/nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=$username dbname=$database' $database);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("full_buf2 = @$full_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");
print("We just invoked the ./nc spock node-create n1 command\n");


my $cmd3 = qq($n1/nodectl spock repset-create $repset $database);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("full_buf3 = @$full_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");
print("We just created the replication set (demo-repset\n");

#
# Test
#
print("We've just created and registered node 1.\n");

my $substring = "create";
if(index($full_buf3, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}
