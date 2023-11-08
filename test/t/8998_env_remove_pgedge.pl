# This test case cleans up after the schedule that builds a two-node cluster  
# The test exercises: ./nodectl remove pgedge
# 
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;



# Remove the pgedge directory

my $cmd3 = qq(rm -rf pgedge);
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
print("I'm removing the pgedge directory with the following command: = $cmd3\n");
print("stdout_buf = @$stdout_buf3\n");
print ("The pgedge directory should be gone now.\n");

# Remove the ~/.pgpass file

my $cmd4 = qq(sudo rm ~/.pgpass);
print("cmd4 = $cmd4");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);
print("I'm removing the .pgpass file with the following command: = $cmd4\n");
print("stdout_buf = @$stdout_buf4\n");
print ("The pgpass file should be gone now.\n");
print ("We're checking to see if the $ENV{EDGE_N1} directory still exists.\n");

if(defined($ENV{EDGE_N1}) && length($ENV{EDGE_N1}) > 0)
{
    exit(0);
}
{
    exit(1);
}
