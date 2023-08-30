# This test case is part of a series that checks for errors caused by missing parameters when calling
# the spock node-create command.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


#
# Call spock node-create without a node name: 
#

my $cmd2 = qq(./nodectl spock node-create 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("We just invoked the ./nc spock node-create n1 command but without a node name.\n");
print("error_message2 = $error_message2\n");
#

if(contains($error_message2, "exited"))

{
    exit(0);
}
else
{
    exit(1);
}







