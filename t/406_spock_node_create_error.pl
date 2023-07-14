# This test case walks through the steps in the Getting Started Guide to create a replicating two-node
# cluster.  I'll use it as a starting point for tests that check spock error handling.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default).
# 

my $cmd = qq(./nodectl cluster create-local demo 2 --pg 16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");
print("This s/b a 2 node cluster named demo, owned by lcdb, with a db named lcdb.  The nodes are named n1/n2.\n");
print("This test assumes they're running on 6432 and 6433\n");

#
# Register node 1 and the repset entry on n1: 
#

my $cmd2 = qq(./nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb');
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("We just invoked the ./nc spock node-create n1 command but without a cluster name.\n");

#
# Print statements
#

print("error_message2 = $error_message2\n");
print("full_buf2 = @$full_buf2\n");
print("stdout_buf2 = @$stdout_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");

#
print("If the server reports an ERROR for the missing database name, the test succeeded\n");
#

my $substring = "ERROR";
if (index($stdout_buf2, $substring) == -1)

{
  exit(0);
}
else
{
 exit(1);
}








