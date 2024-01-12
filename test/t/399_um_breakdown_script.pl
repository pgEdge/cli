# This test case cleans up after the test: 300_setup_script.pl.  
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


my $username = $ENV{EDGE_USERNAME};
my $password = $ENV{EDGE_PASSWORD};
my $database = $ENV{EDGE_DB};
my $port = $ENV{EDGE_START_PORT};
my $pgversion = $ENV{EDGE_COMPONENT};
my $homedir="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $datadir="$homedir/data/$pgversion";
my $cli = $ENV{EDGE_CLI};


#
# Then, use nodectl to remove the Postgres installation.
#

my $cmd = qq($homedir/$cli remove $pgversion);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Diagnostic print statements
#

print("success = $success\n");
# print("error_message = $error_message\n");
#print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

#
# Then, remove the data directory 
#
if(defined($success)){
    print("Removing the data directory: $datadir \n");
        if (File::Path::remove_tree($datadir)) {
            print("Data directory $datadir removed successfully\n");
        } else {
            return 1;
        }

}
else {
    print("Unable to : $cmd \n @$full_buf \n");
    return 1;
}
#my $result = system("rm -rf $home");

#
# Then, we remove the ~/.pgpass file.
# TODO : This should ideally just remove the entries added by regression suite
#

my $cmd1 = qq(sudo rm ~/.pgpass);
print("cmd1 = $cmd1\n");
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);

if (defined($success1))
{
    exit(0);
}
else
{
    exit(1);
}
