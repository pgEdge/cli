# This test case uses psql to make some changes to the pgbench tables on node 1.
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
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Set up pgbench on node 1

my $cmd15 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
print("stdout_buf15 = @$stdout_buf15\n");

my $cmd16 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);
print("stdout_buf16 = @$stdout_buf16\n");

my $cmd17 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);
print("stdout_buf17 = @$stdout_buf17\n");

# Then, confirm that a record has been modified.

print("We just created the pgbench artifacts on ($n1) and are now setting LOG_OLD_VALUE to true.\n");

if(contains(@$stdout_buf17[0], "ALTER TABLE"))

{
    exit(0);
}
else
{
    exit(1);
}




