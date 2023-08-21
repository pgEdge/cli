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

# Create pgbench artifacts
#

my $cmd13 = qq($n2/$version/bin/pgbench -i --port 6433 $database);
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);

print("We've just created pgbench artifacts on = {$n2}\n");

my $cmd14 = qq($n1/$version/bin/pgbench -i --port 6432 $database);
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);

print("We've just created pgbench artifacts on = {$n1}\n");
print("success 14 = $success14\n");
print("stdout_buf14 = @$stdout_buf14\n");

my $substring = "stdout_buf";
if(index($stdout_buf14, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}



