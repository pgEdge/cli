# This test case cleans up after the test: 900_cluster_setup_script_v15.pl.  
#
# We remove the PG installation, the pgedge directory, and the .pgpass file.
#

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# Remove the pgedge directory.

my $cmd1 = qq(sudo rm -rf pgedge);
print("cmd1 = $cmd1");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

# Then, remove the ~/.pgpass file.

my $cmd2 = qq(sudo rm ~/.pgpass);
print("cmd2 = $cmd2");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

if (defined($success1))
{
    exit(0);
}
else
{
    exit(1);
}
