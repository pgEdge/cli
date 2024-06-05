# This test case will create the necessary setup of node2 of a two or three node cluster.
# It will check for the existance of n1 directory which if exists, its nodectl installed 
# setup would be copied in n2dir rather than having to download it again from repo. 
# If the n1 directory does not exist, it will perform a new download/install from the repo.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use File::Copy;
use lib './t/lib';
use contains;
use edge;


my $n1dir = "$ENV{EDGE_CLUSTER_DIR}/n1";
my $homedir1 = "$n1dir/pgedge";
my $n2dir = "$ENV{EDGE_CLUSTER_DIR}/n2";
my $homedir2 = "$n2dir/pgedge";
my $ncdir = "$ENV{NC_DIR}";
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $exitcode = 0;
my $skipInstall = 0;
my $ncdir_copy = "/tmp/nccopy";


# Check if $n2dir is already present
if (-e $n2dir) {
    print("$n2dir already exists\n");
    # check for the minimum existance of install.py and the extracted pgedge directory
    if (-e "$n2dir/install.py" && -d "$n2dir/pgedge") {
        print "nodectl already installed in $n2dir , exiting with success\n";
        $exitcode = 0;
        $skipInstall = 1; #setting it to 1 for the if condition to equate to false in the download and install section
    }
}
else {

    # Check if $n1dir exists
    if (-e $n1dir) {
        # Copy n1dir to n2dir 
        # Also creating $n2dir
        print("Creating $n2dir\n");
        run_command_and_exit_iferr(qq(mkdir -p $n2dir));

        print("copying $n1dir contents to $n2dir\n");
        # Moving $ncdir to $n2dir (to avoid a multi step copy and delete for delete/cleanup)
        #run_command_and_exit_iferr(qq(mv $ncdir_copy/* $n2dir/ && rm -rf $ncdir_copy));

        run_command_and_exit_iferr(qq(cp -r -T $n1dir/. $n2dir/));

        print "Contents copied from $n1dir to $n2dir\n";
        $skipInstall = 1;
    }
    else {
        print ("$n1dir does not exist, proceeding to download and install pgedge");
        $skipInstall = 0;
    }
}

# skip the curl download and python install.py if its been copied from pre-downloaded nc directory 
if (!$skipInstall)
{
    # Create $n2dir with -p switch
    print("Creating $n2dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n2dir));

    # Download the install.py file into the directory
    print("Download the install.py file into the directory\n");
    run_command_and_exit_iferr(qq(curl -fsSL $ENV{EDGE_REPO} > $n2dir/install.py));

    # Move into the pgedge directory and run the install.py file
    print ("Move into the pgedge directory and run the install.py file\n");
    chdir("./$n2dir");
    run_command_and_exit_iferr(qq(python install.py));

    chdir("pgedge");
    # Pull down pgedge info.
    my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4) = IPC::Cmd::run(command => "./pgedge info", verbose => 0);
    print ("Our version is:\n @$stdout_buf4\n");

    chdir("./../../../../");
}

exit ($exitcode);
