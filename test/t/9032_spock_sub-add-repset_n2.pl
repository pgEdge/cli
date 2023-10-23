# In this test case, we add the replication set to the subscription on node 2.
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
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We retrieve info for node 2:

my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir = $out3->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port = $out4->[0]->{"port"};
print("The port number is {$port}\n");

my $cmd24 = qq($homedir/nodectl spock sub-add-repset sub_n2n1 $repset $database);
print("cmd24 = $cmd24\n");
my($success24, $error_message24, $full_buf24, $stdout_buf24, $stderr_buf24)= IPC::Cmd::run(command => $cmd24, verbose => 0);

print("success24 = $success24\n");
print("stdout_buf24 = @$stdout_buf24\n");

# Use psql to query the spock.replication_set_table table to confirm that the pgbench tables are added:

print("We just added the pgbench tables to the replication set on ($n2).\n");

my $cmd20 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.subscription");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
print("stdout_buf20 = (@$stdout_buf20)\n");

if(contains(@$stdout_buf20[0], "sub_n2n1"))

{
    exit(0);
}
else
{
    exit(1);

}



