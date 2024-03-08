# This test case removes pgedge from the node 2 (n2) and will be used as a cleanup script
# for the 8001a and 8001b tests.  
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
my $n2dir = "$ENV{EDGE_CLUSTER_DIR}/n2";
my $homedir2 = "$n2dir/pgedge";
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $datadir2="$homedir2/data/$pgversion";
#my $pgpassEntry = "*:*:*:$username:$password";
my $exitcode = 0;


# Remove pgedge
print("Removing pgedge on node 2\n");
run_command_and_exit_iferr(qq($homedir2/$cli remove $pgversion --rm-data));
print("Verifying $pgversion , $spver , $spver are removed from node 2\n");
#check for pgV
my $cmd = qq($homedir2/$cli um list);
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success) && !is_umlist_component_installed($stdout_buf, "$pgversion")) 
{
    print("cmd = $cmd\n");
    $exitcode++;
} 

#check for spock
my $cmd2 = qq($homedir2/$cli um list);
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success2) && !is_umlist_component_installed($stdout_buf2, "$spockversion")) 
{
    $exitcode++;
} 

#check for snowflake
my $cmd3 = qq($homedir2/$cli um list);
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= run_command($cmd);
#print("stdout : @$full_buf \n");
if (defined($success3) && !is_umlist_component_installed($stdout_buf3, "$snowflakeversion")) 
{
    $exitcode++;
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
