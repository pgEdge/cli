# This test case cleans up after the test: 600_cluster_setup_script_v15.pl.  
# The test exercises: ./nodectl cluster destroy-local
# We remove the PG installation and the pgedge directory.
#

use strict;
use warnings;

use File::Which;
use File::Path;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory
#
chdir ("./pgedge");

#
# Get the location of the home directory before removing pgEdge; store it in $home.
#

my $out = decode_json(`./nc --json info`);
my $home = $out->[0]->{"home"};
print("the home directory is = {$home}\n");

print("home = $home\n");

#
# Then, use nodectl to remove the Postgres installation.
#

my $cmd = qq(./nodectl cluster destroy demo);
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

my $result = system("rm -rf $home");

#
# Then, we remove the ~/.pgpass file.
#

#my $cmd1 = qq(sudo rm ~/.pgpass);
#print("cmd1 = $cmd1");
#my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if (defined($success))
{
    exit(0);
}
else
{
    exit(1);
}    
    
