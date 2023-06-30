# This test case cleans up after the test: 300_setup_script.pl 
# The test exercises: ./nodectl remove pgedge
# We remove the PG installation, the pgedge directory, and the  ~/.pgpass file.
#

use strict;
use warnings;

use File::Which;
use NodeCtl;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
# chdir("./pgedge");

#
# Get the location of the data directory and home directory before removing pgEdge; store them in $datadir and $home.
#

my $nc = NodeCtl::get_new_nc("/tmp/nodectl_dir");
print("get_new_nc returned");
my $datadir = $nc->get_info_item_pg16("datadir");
print("get_info_item_pg16 returned");
my $home = $nc->get_home_dir();

print("datadir = $datadir\n");
print("home = $home\n");

#
# Move into the pgedge directory.
#
 chdir("./pgedge");




#
# Then, use nodectl to remove the Postgres installation.
#

my $cmd = qq(./nodectl remove pgedge);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Then, remove the data directory and the contents of the pgedge directory; then the pgedge directory is deleted.
#

File::Path::remove_tree($datadir);

my $result = system("rm -rf $home");

#
# Then, we remove the ~/.pgpass file.
#

my $cmd1 = qq(sudo rm ~/.pgpass);
#print("cmd1 = $cmd1");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if (defined($success))
{
    exit(0);
}
else
{
    exit(1);
}
