# This test is part of a series of test that confirm that spock node-create fails gracefully if not 
# passed the correct parameters.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


# Call spock node-create without a trailing cluster name: 
#

my $cmd2 = qq(./nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb');
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("We just invoked the ./nc spock node-create n1 command but without a cluster name.\n");
print("stdout_buf2 = @$stdout_buf2\n");
print("If the server reports an ERROR for the missing database name, the test succeeded\n");

if(contains($error_message2, "exited"))

{
    exit(0);
}
else
{
    exit(1);
}









