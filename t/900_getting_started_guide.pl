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
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default).
# 

my $cmd = qq(./nodectl cluster create-local $cluster 2 --$version -U $username -P $password -d $database);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");

# Test to confirm that cluster is set up.
#

print("success = $success\n");
print("stdout_buf = @$stdout_buf\n");
print("full_buf = @$full_buf\n");
print("This step installs Postgres and creates a 2 node cluster.\n");

my $substring = "EXTENSION";
if(index($stdout_buf, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}




