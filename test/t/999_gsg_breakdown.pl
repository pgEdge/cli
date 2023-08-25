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

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
print("my json = $json2");
my $out2 = decode_json($json2);
my $datadir = $out2->[0]->{"datadir"};
print("The data directory is {$datadir}\n");

# Move into the pgedge directory
chdir ("./pgedge");

# Then, use nodectl to remove the Postgres installation.

my $cmd = qq($n1/pgedge/nodectl cluster destroy-local demo);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

# Diagnostic print statements

print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");

# Then, remove the data directory and the contents of the pgedge directory; then the pgedge directory is deleted.

File::Path::remove_tree($datadir);

my $result = system("rm -rf $homedir");

# Then, remove the ~/.pgpass file.

my $cmd1 = qq(sudo rm ~/.pgpass);
print("cmd1 = $cmd1");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0)
;

if (defined($success))
{
    exit(0);
}
else
{
    exit(1);
}
    
