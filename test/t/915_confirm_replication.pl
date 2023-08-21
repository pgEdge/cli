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
# Test to see if replication is working on node 1
#

my $cmd29 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6433 -d $database -c "SELECT filler FROM pgbench_tellers WHERE tid = 1");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);

print("success29 = $success29\n");
print("stdout_buf29 = @$stdout_buf29\n");
print("If the word test is in @$stdout_buf29 we've confirmed replication is working!\n");

my $substring = "test";
if(index($stdout_buf29, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}

