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
# Create the subscription on node 2
#

my $cmd12 = qq($n2/nodectl spock sub-create sub_n2n1 'host=127.0.0.1 port=6432 user=$username dbname=$database' $database);
print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
print("success12 = $success12\n");
print("stdout_buf12 = @$stdout_buf12\n");

#
# Test
#
my $substring = "sub_create";
if(index($stdout_buf12, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}


