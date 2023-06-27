# This test case cleans up after the test: 300_setup_script.pl 
# The test exercises: ./nodectl remove pgedge
# We remove the PG installation, the pgedge directory, and the  ~/.pgpass file.
#

use strict;
use warnings;

use File::Which;
use PostgreSQL::Test::Cluster;
use PostgreSQL::Test::Utils;
use Test::More tests => 1;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use NodeCtl;

#
# Get the location of the data directory and home directory before removing pgEdge; store them in $datadir and $home.
#

my $nc = NodeCtl::get_new_nc("/tmp/nodectl_dir");
diag("get_new_nc returned");
my $datadir = $nc->get_info_item_pg16("datadir");
diag("get_info_item_pg16 returned");
my $home = $nc->get_home_dir();

diag("datadir = $datadir\n");
diag("home = $home\n");

#
# Then, use nodectl to remove the Postgres installation.
#

my $cmd = qq(./nodectl remove pgedge);
diag("cmd = $cmd\n");
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
#diag("cmd1 = $cmd1");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if (defined($success))
{
    ok(1);
}
else
{
    ok(0);
}

done_testing();
