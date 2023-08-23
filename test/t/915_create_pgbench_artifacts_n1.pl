# In this test case, we create the pgbench artifacts on node 1.
#

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
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2";

# Node 1:
# We can retrieve the home directory from nodectl in json form...
my $json = `$n1/pgedge/nc --json info`;
print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Create pgbench artifacts on Node 1:

my $cmd13 = qq($homedir/$version/bin/pgbench -i --port $port $database);
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
print("We've just created pgbench artifacts on = {$n1}\n");

# Then, we connect with psql and confirm that a table named pgbench_accounts exists.

my $cmd7 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pgbench_accounts ORDER BY aid LIMIT 10");
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




