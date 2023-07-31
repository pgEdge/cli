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
# Use psql to check the setup, and confirm replication is working.
#

my $cmd25 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "SELECT * FROM spock.node");
print("cmd25 = $cmd25\n");
my($success25, $error_message25, $full_buf25, $stdout_buf25, $stderr_buf25)= IPC::Cmd::run(command => $cmd25, verbose => 0);

print("success25 = $success25\n");
print("stdout_buf25 = @$stdout_buf25\n");

my $cmd26 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription");
print("cmd26 = $cmd26\n");
my($success26, $error_message26, $full_buf26, $stdout_buf26, $stderr_buf26)= IPC::Cmd::run(command => $cmd26, verbose => 0);

print("success26 = $success26\n");
print("stdout_buf26 = @$stdout_buf26\n");

my $cmd27 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "SELECT * FROM pgbench_tellers WHERE tid = 1");
print("cmd27 = $cmd27\n");
my($success27, $error_message27, $full_buf27, $stdout_buf27, $stderr_buf27)= IPC::Cmd::run(command => $cmd27, verbose => 0);

print("success27 = $success27\n");
print("stdout_buf27 = @$stdout_buf27\n");

my $cmd28 = qq($n1/$version/bin/psql -t -h 127.0.0.1 -p 6432 -d $database -c "UPDATE pgbench_tellers SET filler = 'test' WHERE tid = 1");
print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);

print("success28 = $success28\n");
print("stdout_buf28 = @$stdout_buf28\n");

#
# Test
#

print("$success28 is the value in success");
print("If the word UPDATE is in @$stdout_buf28 we've updated the pgbench_tellers table!\n");

my $substring = "UPDATE";
if(index($stdout_buf28, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}














