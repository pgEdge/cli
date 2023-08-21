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

#
# Then, add the repsets to the subscriptions:
#

my $cmd23 = qq($n1/nodectl spock sub-add-repset sub_n1n2 $repset $database);
print("cmd23 = $cmd23\n");
my($success23, $error_message23, $full_buf23, $stdout_buf23, $stderr_buf23)= IPC::Cmd::run(command => $cmd23, verbose => 0);

print("success23 = $success23\n");
print("stdout_buf23 = @$stdout_buf23\n");

my $cmd24 = qq($n2/nodectl spock sub-add-repset sub_n2n1 $repset $database);
print("cmd24 = $cmd24\n");
my($success24, $error_message24, $full_buf24, $stdout_buf24, $stderr_buf24)= IPC::Cmd::run(command => $cmd24, verbose => 0);

print("success24 = $success24\n");
print("stdout_buf24 = @$stdout_buf24\n");

#
# Test
#

print("success24 = $success24\n");
print("stdout_buf24 = @$stdout_buf24\n");
print("If the word sub_add_repset is in @$stdout_buf24 we've added the repsets to the subscriptions!\n");

my $substring = "sub_add_repset";
if(index($stdout_buf24, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}



