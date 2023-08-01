# This test case cleans up after the test: 405_spock_node_create_error.pl  
# The test exercises: ./nodectl remove pgedge
# We remove the PG installation, the pgedge directory, and the  ~/.pgpass file.
#

use strict;
use warnings;

use File::Which;
use File::Path;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Get the location of the data directory and home directory before removing pgEdge; store them in $datadir and $home.
#

my $out = decode_json(`./pgedge/nc --json info`);
my $home = $out->[0]->{"home"};
print("the home directory is = {$home}\n");

my $out1 = decode_json(`./pgedge/nc --json info pg16`);
my $datadir = $out1->[0]->{"datadir"};
print("the data directory is = {$datadir}\n");

print("datadir = $datadir\n");
print("home = $home\n");

#
# Then, use nodectl to remove the Postgres installation.
#

my $cmd = qq(./pgedge nodectl remove pgedge);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Diagnostic print statements
#

print("success = $success\n");
# print("error_message = $error_message\n");
print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

#
# Then, remove the data directory and the contents of the pgedge directory; then the pgedge directory is deleted.
#

File::Path::remove_tree($datadir);

my $result = system("rm -rf $home");

if (defined($success))
{
    exit(1);
}
else
{
    exit(0);
}
