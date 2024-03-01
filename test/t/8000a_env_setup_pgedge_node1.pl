# This test case will create the necessary setup of node1 of a two-node cluster.
# It will check for the existance of nc directory that if exists would have 
# the necessary nodectl setup that can be copied in n1 rather than having to
# download it again. If the nc directory does not exist, it will perform a new
# download. 

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
my $ncdir = "$ENV{NC_DIR}";
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $exitcode = 0;
my $skipInstall = 0;
my $ncdir_copy = "/tmp/nccopy";

# Check if $n1dir is already present
if (-e $n1dir) {
    print("$n1dir already exists\n");
    # check for the minimum existance of install.py and the extracted pgedge directory
    if (-e "$n1dir/install.py" && -d "$n1dir/pgedge") {
        print "nodectl already installed in $n1dir , exiting\n";
        $exitcode = 0;
        $skipInstall = 1; #setting it to 1 for the if condition to equate to false in the download and install section
    }
}
else {
    

    # Check if $ncdir exists
    if (-e $ncdir) {

        # Copying $ncdir contets to a temp location since the $n1dir resides inside 
        # $ncdir, and a direct cp -r $ncdir/* $n1dir/ wasn't possible. 
        # Also creating $n1dir
        print("Creating $n1dir\n");
        run_command_and_exit_iferr(qq(rm -rf $ncdir_copy && cp -r -T $ncdir/. $ncdir_copy && mkdir -p $n1dir));

        print("copying $ncdir contents to $n1dir\n");
        # Copy $ncdir () to $n1dir
        run_command_and_exit_iferr(qq(mv $ncdir_copy/* $n1dir/));

        print "Contents copied from $ncdir to $n1dir\n";
        $skipInstall = 1;
    }
    else {
        print ("$ncdir does not exist, proceeding to download and install pgedge");
        $skipInstall = 0;
    }
}

# skip the curl download and python install.py if its been copied from pre-downloaded nc directory 
if (!$skipInstall)
{
    # Create $n1dir with -p switch
    print("Creating $n1dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n1dir));

    # Download the install.py file into the directory
    print("Download the install.py file into the directory\n");
    run_command_and_exit_iferr(qq(curl -fsSL $ENV{EDGE_REPO} > $n1dir/install.py));

    # Move into the pgedge directory and run the install.py file
    print ("Move into the pgedge directory and run the install.py file\n");
    chdir("./$n1dir");
    run_command_and_exit_iferr(qq(python install.py));
    chdir("./../../../../");
}

exit ($exitcode);









