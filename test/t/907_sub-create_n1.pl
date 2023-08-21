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

# Then, create the subscription on node 1:

my $cmd11 = qq($n1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 port=6433 user=$username dbname=$database' $database);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);

print("success11 = $success11\n");
print("stdout_buf11 = @$stdout_buf11\n");

#
# Test
#
my $substring = "sub_create";
if(index($stdout_buf11, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}





























