# This test case runs the command:
# ./nc service stop -c pg16
#

use strict;
use warnings;

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $cmd1 = qq(pwd);
print("my? = $cmd1\n");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);
print("stdout_buf1 = @$stdout_buf1\n");
print("my pwd = @$stdout_buf1\n");

#
# Move into the pgedge directory.
#
chdir("./pgedge");

#
# This test stops the service, then tests the stdout_buf array for the word 'stopping'. 

my $cmd = qq(./nc service stop -c pg16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

if(contains(@$stdout_buf[0], "stopping"))

{
    exit(0);
}
else
{
    exit(1);
}



