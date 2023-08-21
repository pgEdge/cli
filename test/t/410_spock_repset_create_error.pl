# This test case exercises the spock repset-create command, but omits the name of the repset when 
# calling the command; it should throw an error.
# 
# This test is part of a test sequence: 020, 410, 411, 412, and 414.  

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
# Create a variable with the path to each node.
# 

my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1"; 
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2";

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
# Register node 1: 
#

my $cmd2 = qq($n1/nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("full_buf2 = @$full_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");
print("We just invoked the ./nc spock node-create n1 command\n");

#
# This command creates a repset if provided with a replication set name and a database name; we are 
# omitting the replication set name to throw an error.
#

my $cmd3 = qq($n1/nodectl spock repset-create lcdb);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("error_message3 = $error_message3\n");
print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");

#
print("If the server reports an ERROR for the missing node name, the test succeeded\n");
#

my $substring = "ERROR";
if (index($stdout_buf3, $substring) == -1)

{
  exit(0);
}
else
{
 exit(1);
}


















