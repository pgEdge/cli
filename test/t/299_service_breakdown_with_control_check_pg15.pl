# This test case cleans up after the test: 200_setup_script.pl.  
# The test exercises: ./nodectl remove pgedge
# We remove the PG installation
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib '../lib';
use contains;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/nodectl";

# Move into the pgedge directory

chdir ("./pgedge");

# Get the location of the data directory and home directory before removing pgEdge; store them in $datadir and $home.

my $json_info = decode_json(`./nc --json info`);
my $home = $json_info->[0]->{"home"};
print("the home directory is = {$home}\n");

my $out2 = decode_json(`./nc --json info pg15`);
my $datadir = $out2->[0]->{"datadir"};
print("the data directory is = {$datadir}\n");

print("datadir = $datadir\n");
print("home = $home\n");

sub remove_pgedge_leave_data
{
    if (defined $home && length $home > 0)
    {
        print ("pgedge exists\n");
        # Then, use nodectl to remove the pgEdge/Postgres installation; this command leaves the data directory intact.     
        my $cmd = qq(./nodectl remove pgedge);
        print("I'm removing the pgEdge installation with the following command: = $cmd\n");
        my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0); 
        print("stdout_buf = @$stdout_buf\n");
        print ("pgEdge platform should be gone now. \n");
    }	    
    else
    {
	exit(1);
    }
}

sub remove_data_dir
{
    if (defined $datadir && length $datadir > 0)
    {
        print("the data directory is = {$datadir}\n");
        # Remove the data directory
        my $cmd2 = qq(rm -rf $datadir);
        print("I'm removing the data directory with the following command: = $cmd2\n");
        my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
	print("stdout_buf = @$stdout_buf\n");
	print ("The data directory should be gone now.\n");
    }
    else
    {
	exit(1);
    }
}

sub remove_home_dir
{
    if (defined $home && length $home > 0)
    {
        print ("The home directory remains");
    
    # Remove the home directory and the .pgpass file
    
        my $cmd3 = qq(rm -rf $home);
        #print("cmd3 = $cmd3\n");
        my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
        print("I'm removing the home directory with the following command: = $cmd3\n");
        print("stdout_buf = @$stdout_buf\n");
        print ("The $home directory should be gone now.\n");

        my $cmd4 = qq(sudo rm ~/.pgpass);
        print("cmd4 = $cmd4");
        my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);
        print("I'm removing the data directory with the following command: = $cmd4\n");
        print("stdout_buf = @$stdout_buf\n");
        print ("The pgpass file should be gone now.\n");

	exit(0);
    }
    {
	exit(1);
    }
}


remove_pgedge_leave_data();
remove_data_dir();
remove_home_dir();
remove_pgpass();

