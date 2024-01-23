# This test case will create the necessary setup of node2 of a two-node cluster.
# It will check for the existance of nc directory that if exists would have 
<<<<<<< HEAD
# the necessary nodectl setup that can be copied in n2 rather than having to
=======
# the necessary nodectl setup that can be copied in n1 rather than having to
>>>>>>> REL24_1
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



my $n2dir = "$ENV{EDGE_CLUSTER_DIR}/n2";
my $homedir2 = "$n2dir/pgedge";
<<<<<<< HEAD
my $ncdir = "$ENV{NC_DIR}";
=======
my $ncdir = "$ENV{EDGE_HOME_DIR}/nc";
>>>>>>> REL24_1
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $exitcode = 0;
my $skipInstall = 0;
<<<<<<< HEAD
my $ncdir_copy = "/tmp/nccopy";
=======
>>>>>>> REL24_1


# Check if $n2dir is already present
if (-e $n2dir) {
    print("$n2dir already exists\n");
    # check for the minimum existance of install.py and the extracted pgedge directory
    if (-e "$n2dir/install.py" && -d "$n2dir/pgedge") {
<<<<<<< HEAD
        print "nodectl already installed in $n2dir , exiting with success\n";
=======
        print "nodectl already installed in $n2dir , exiting\n";
>>>>>>> REL24_1
        $exitcode = 0;
        $skipInstall = 1; #setting it to 1 for the if condition to equate to false in the download and install section
    }
}
else {
<<<<<<< HEAD

    # Check if $ncdir exists
    if (-e $ncdir) {
        # Re-using the $ncdir_copy that has a copy of $ncdir placed by 8000a test 
        # and mv it to the $n2dir now that it wont further be required in the tmp swap location 
        # Also creating $n2dir
        print("Creating $n2dir\n");
        run_command_and_exit_iferr(qq(mkdir -p $n2dir));

        print("copying $ncdir contents to $n2dir\n");
        # Moving $ncdir to $n2dir (to avoid a multi step copy and delete for delete/cleanup)
        run_command_and_exit_iferr(qq(mv $ncdir_copy/* $n2dir/ && rm -rf $ncdir_copy));
=======
    # Create $n2dir with -p switch
    print("Creating $n2dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n2dir));

    # Check if $ncdir exists
    if (-e $ncdir) {
        print("$ncdir already exists, copying its concents to $n2dir\n");
        # Copy everything under $ncdir to $n2dir
        run_command_and_exit_iferr(qq(cp -r $ncdir/* $n2dir/));
>>>>>>> REL24_1

        print "Contents copied from $ncdir to $n2dir\n";
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
<<<<<<< HEAD
    # Create $n2dir with -p switch
    print("Creating $n2dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n2dir));

=======
>>>>>>> REL24_1
    # Download the install.py file into the directory
    print("Download the install.py file into the directory\n");
    run_command_and_exit_iferr(qq(curl -fsSL $ENV{EDGE_REPO} > $n2dir/install.py));

    # Move into the pgedge directory and run the install.py file
    print ("Move into the pgedge directory and run the install.py file\n");
    chdir("./$n2dir");
    run_command_and_exit_iferr(qq(python install.py));
    chdir("./../../../../");
}

exit ($exitcode);
