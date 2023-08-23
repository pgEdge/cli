# This test case confirms that the row updated in test t/914 is correctly 
# replicated on node 2.

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

# We can retrieve the home directory from nodectl in json form...
my $json = `$n2/pgedge/nc --json info`;
print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n2/pgedge/nc --json info pg16`;
print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Test to see if replication is working on node 2

my $cmd29 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);
print("stdout_buf = @$stdout_buf29\n");

print("If the word test is in our search string (@$stdout_buf29) we've confirmed replication is working as expected; if it isn't
	there, this test will fail!\n");

# Test for the search_term in a buffer.

if (contains(@$stdout_buf29[0], "test"))

{
    exit(0);
}
else
{
    exit(1);
}

