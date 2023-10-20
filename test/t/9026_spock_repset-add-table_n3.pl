# This test adds the pgbench tables to the replication set on node 2.
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
my $n3 = "~/work/nodectl/test/pgedge/cluster/demo/n3";

# We retrieve the home directory from nodectl in json form... 
my $json3 = `$n3/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir = $out3->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n3/pgedge/nc --json info pg16`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port = $out4->[0]->{"port"};
print("The port number is {$port}\n");

# Then, on node 3, invoke spock repset-add-table to add pgbench tables to the repset:

my $cmd22 = qq($homedir/nodectl spock repset-add-table $repset 'pgbench_*' $database);
print("cmd22 = $cmd22\n");
my($success22, $error_message22, $full_buf22, $stdout_buf22, $stderr_buf22)= IPC::Cmd::run(command => $cmd22, verbose => 0);
print("stdout_buf22 = @$stdout_buf22\n");

# Then, confirm that a record has been modified.

print("We just added the pgbench tables to the replication set on ($n2).\n");

my $cmd20 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
print("stdout_buf20 = (@$stdout_buf20)\n");

if(contains(@$stdout_buf20[0], "ALTER TABLE"))

{
    exit(0);
}
else
{
    exit(1);

}

