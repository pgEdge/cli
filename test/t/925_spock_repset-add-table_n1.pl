# This test adds the pgbench tables to the replication set on node 1.
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

# On node 1:
# ==========
# We can retrieve the home directory from nodectl in json form...i
#
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

# Then, on node 1, invoke spock repset-add-table to add pgbench tables to the repset:

my $cmd21 = qq($homedir/nodectl spock repset-add-table $repset 'pgbench_*' $database);
print("cmd21 = $cmd21\n");
my($success21, $error_message21, $full_buf21, $stdout_buf21, $stderr_buf21)= IPC::Cmd::run(command => $cmd21, verbose => 0);
print("stdout_buf21 = @$stdout_buf21\n");

# Use psql to query the spock.replication_set_table table to confirm that the pgbench tables are added:

print("We just added the pgbench tables to the replication set on ($n1).\n");

my $cmd20 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set_table");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
print("stdout_buf20 = (@$stdout_buf20)\n");

if(contains(@$stdout_buf20[0], "pgbench_accounts"))

{
    exit(0);
}
else
{
    exit(1);

}

