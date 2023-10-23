# This script configures pgbench on node 2.

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

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n2/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n2/pgedge/nc --json info $version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Set up pgbench on node 2

my $cmd18 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd18 = $cmd18\n");
my($success18, $error_message18, $full_buf18, $stdout_buf18, $stderr_buf18)= IPC::Cmd::run(command => $cmd18, verbose => 0);
print("stdout_buf18 = @$stdout_buf18\n");

my $cmd19 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd19 = $cmd19\n");
my($success19, $error_message19, $full_buf19, $stdout_buf19, $stderr_buf19)= IPC::Cmd::run(command => $cmd19, verbose => 0);
print("stdout_buf19 = @$stdout_buf19\n");

my $cmd20 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
print("stdout_buf20 = (@$stdout_buf20)\n");

# Then, confirm that a record has been modified.

print("We just created the pgbench artifacts on ($n2) and are now setting LOG_OLD_VALUE to true.\n");

if(contains(@$stdout_buf20[0], "ALTER TABLE"))

{
    exit(0);
}
else
{
    exit(1);

}
