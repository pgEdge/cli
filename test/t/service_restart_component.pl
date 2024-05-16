# This test case runs the command:
# ./nc service restart pgV
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $homedir = "$ENV{EDGE_HOME_DIR}";
my $cli = $ENV{EDGE_CLI};
my $pgversion = $ENV{EDGE_COMPONENT};


#
# We use nodectl to service restart pg16.
# 

my $cmd = qq($homedir/$cli service restart $pgversion);
print("cmd = $cmd\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
print("stdout_buf : @$stdout_buf");

# A successfull restart (with pgV running as a systemctl service) it returns the following four lines:
# pg16 stopping 
# #sudo systemctl stop pg16 
# pg16 starting on port 6432
# #sudo systemctl start pg16

# Combine trimmed lines into a single string as the \n in the output seems to change order of output.
# map processes each element of @$stdout_buf using the sanitize_and_combine_multiline_stdout function.
# join combines the processed elements into a single string.

@$stdout_buf = join(' ', map { sanitize_and_combine_multiline_stdout($_) } @$stdout_buf);

if (contains($stdout_buf->[0], "stop") && contains($stdout_buf->[0], "start"))
{
    exit(0);
}
else
{
    exit(1);
}

