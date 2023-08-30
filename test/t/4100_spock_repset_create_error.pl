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
use lib './t/lib';
use contains;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# Register node 1:

my $cmd2 = qq(./nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("full_buf2 = @$full_buf2\n");

#
# This command creates a repset if provided with a replication set name and a database name; we are 
# omitting the replication set name to throw an error.

my $cmd3 = qq(./nodectl spock repset-create lcdb);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
print("stdout_buf3 = @$stdout_buf3\n");

if(contains($error_message3, "exited"))

{
    exit(0);
}
else
{
    exit(1);
}
