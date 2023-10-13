# This test case runs the command:
# ./nc service status 
#

use strict;
use warnings;

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './lib';
use contains;

#
# Move into the pgedge directory.
#
chdir("./pgedge");

#
# This test stops the service, then tests the stdout_buf array for the word 'stopping'. 

my $cmd = qq(./nc service status );
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("stdout_buf = @$stdout_buf\n");


