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
# Set up pgbench on node 2
#

my $cmd18 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6433 -d $database -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd18 = $cmd18\n");
my($success18, $error_message18, $full_buf18, $stdout_buf18, $stderr_buf18)= IPC::Cmd::run(command => $cmd18, verbose => 0);

print("success18 = $success18\n");
print("full_buf18 = @$full_buf18\n");
print("stdout_buf18 = @$stdout_buf18\n");

my $cmd19 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6433 -d $database -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd19 = $cmd19\n");
my($success19, $error_message19, $full_buf19, $stdout_buf19, $stderr_buf19)= IPC::Cmd::run(command => $cmd19, verbose => 0);

print("success19 = $success19\n");
print("full_buf19 = @$full_buf19\n");
print("stdout_buf19 = @$stdout_buf19\n");

my $cmd20 = qq($n2/$version/bin/psql -t -h 127.0.0.1 -p 6433 -d $database -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);

print("success20 = $success20\n");
print("full_buf20 = @$full_buf20\n");
print("stdout_buf20 = @$stdout_buf20\n");

#
# Test
#

print("$success20 is the value in success");
print("If the word ALTER is in @$stdout_buf20 we've updated the table!\n");

my $substring = "ALTER";
if(index($stdout_buf20, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}














#
# Test
#

if (defined($success20))
{
    exit(1);
}
else
{
    exit(0);
}





