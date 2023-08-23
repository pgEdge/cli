# This test case is part of a series that checks for errors caused by missing parameters when calling
# the spock node-create command.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;


#
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default).
# 

my $cmd = qq(./pgedge/nodectl cluster create-local demo 2 --pg 16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");
print("This s/b a 2 node cluster named demo, owned by lcdb, with a db named lcdb.  The nodes are named n1/n2.\n");
print("This test assumes they're running on 6432 and 6433\n");

#
# Call spock node-create without a node name: 
#

my $cmd2 = qq(./pgedge/nodectl spock node-create 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("We just invoked the ./nc spock node-create n1 command but without a node name.\n");

#
# Print statements
#

print("error_message2 = $error_message2\n");
print("full_buf2 = @$full_buf2\n");
print("stdout_buf2 = @$stdout_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");

#
print("If the server reports an ERROR for the missing node name, the test succeeded\n");
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








