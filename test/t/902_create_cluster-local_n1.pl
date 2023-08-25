# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
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

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default).
# 

my $cmd = qq(./nodectl cluster create-local $cluster 2 -U $username -P $password -d $database --$version);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");



# Test to confirm that cluster is set up.
#
# Check the installation properties of node 1 and node 2

# We can retrieve the home directory from nodectl in json form...
my $json = `$n1/pgedge/nc --json info`;
print("This is from node 1: = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
print("This is also from node 1: = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

my $cmd29 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pg_available_extensions WHERE name = 'spock'");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);
print("stdout_buf on node 1: = @$stdout_buf29\n");

print("If the word test is in our search string (@$stdout_buf29) we've confirmed replication is working as expected; if it isn't
        there, this test will fail!\n");

# Test for the search_term in a buffer.

if (contains(@$stdout_buf29[0], "3.1"))

{
    exit(0);
}
else
{
    exit(1);
}
