# This test case removes pgedge from the node 3 (n3) and will be used as a cleanup script
# for the 8002a and 8002b tests.  
# The test exercises: ./nodectl remove pgedge
# 
#

use strict;
use warnings;
use File::Path;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;

my $username = $ENV{EDGE_USERNAME};
my $password = $ENV{EDGE_PASSWORD};
my $n3dir = "$ENV{EDGE_CLUSTER_DIR}/n3";
my $homedir3 = "$n3dir/pgedge";
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $datadir3="$homedir3/data/$pgversion";
#my $pgpassEntry = "*:*:*:$username:$password";
my $exitcode = 0;


# Remove pgedge
print("Removing pgedge on node 3\n");
run_command_and_exit_iferr(qq($homedir3/$cli remove pgedge --pg $ENV{EDGE_INST_VERSION}));
print("Verifying $pgversion , $spver , $spver are removed from node 3\n");
#check for pgV
my $cmd = qq($homedir3/$cli um list);
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success) && !is_umlist_component_installed($stdout_buf, "$pgversion")) 
{
    print("cmd = $cmd\n");
    $exitcode++;
} 

#check for spock
my $cmd2 = qq($homedir3/$cli um list);
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success2) && !is_umlist_component_installed($stdout_buf2, "$spockversion")) 
{
    $exitcode++;
} 

#check for snowflake
my $cmd3 = qq($homedir3/$cli um list);
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success3) && !is_umlist_component_installed($stdout_buf3, "$snowflakeversion")) 
{
    $exitcode++;
} 

# Cleanup. Removing datadir and the pgpass entry done by the 8000 tests

print("Removing the data directory: $datadir3 \n");
if (File::Path::remove_tree($datadir3)) {
    print("Data directory $datadir3 removed successfully\n");
} else {
    print("Unable to remove Data directory $datadir3\n");
}

# removing the pgpass file that was created in 8000 test
my $cmd4 = qq(rm ~/.pgpass);
print("cmd = $cmd4\n");
run_command($cmd4);
if ($exitcode==3)
{
    exit (0);
}
else 
{
    exit(1);
}

=pod
# pgpass enhancement in future that only removes the entry rather than whole file
# Check if .pgpass file exists
if (-e "~/.pgpass") {
    # Create a temporary file to store modified content
    my $tempFile = "/tmp/pgpass_temp";
    
    # Read the content of .pgpass file, remove the matching entry, and write to the temporary file
    run_command_and_exit_iferr(qq(grep -v "$pgpassEntry" ~/.pgpass > $tempFile));

    # Move the temporary file back to .pgpass
    run_command_and_exit_iferr(qq(mv $tempFile ~/.pgpass));

    print("Entry removed from .pgpass file\n");
}
else {
    print(".pgpass file not found\n");
}
=cut
