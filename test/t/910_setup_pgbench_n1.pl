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
# Set up pgbench on node 1
#

my $cmd15 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);

print("success15 = $success15\n");
print("stdout_buf15 = @$stdout_buf15\n");

my $cmd16 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);

print("success16 = $success16\n");
print("stdout_buf16 = @$stdout_buf16\n");

my $cmd17 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);

print("success17 = $success17\n");
print("stdout_buf17 = @$stdout_buf17\n");

#
# Test
#

print("If the word ALTER is in @$stdout_buf17 we've altered the tables on node 1 to set up pgbench!\n");

my $substring = "ALTER";
if(index($full_buf17, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}



