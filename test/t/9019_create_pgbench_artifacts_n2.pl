# In this test case, we create the pgbench artifacts on node 2.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# Node 2:

# We can retrieve the home directory from nodectl in json form...
my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory is {$homedir2}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number is {$port2}\n");

my $cmd14 = qq($homedir2/$version/bin/pgbench -i --port $port2 $database);
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
print("We've just created pgbench artifacts on = {$n2}\n");

my $cmd49 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "select * from pgbench_accounts limit 5");
print("cmd49 = $cmd49\n");
my($success49, $error_message49, $full_buf49, $stdout_buf49, $stderr_buf49)= IPC::Cmd::run(command => $cmd49, verbose => 0);

# If we have a table in the database named pgbench_accounts, this test succeeded.

my $cmd7 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM pgbench_accounts ORDER BY aid LIMIT 10");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

# Then, confirm that the subscription has been created.

print("We just created the pgbench artifacts on ($n1) and are now verifying it exists.\n");

if(contains(@$stdout_buf7[0], "1 |   1 |        0 |"))

{
    exit(0);
}
else
{
    exit(1);
}


