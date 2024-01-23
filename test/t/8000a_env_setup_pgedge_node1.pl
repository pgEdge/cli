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
<<<<<<< HEAD
    

    # Check if $ncdir exists
    if (-e $ncdir) {

        # Copying $ncdir contets to a temp location since the $n1dir resides inside 
        # $ncdir, and a direct cp -r $ncdir/* $ncdir/ wasn't possible. 
        # Also creating $n1dir
        print("Creating $n1dir\n");
        run_command_and_exit_iferr(qq(rm -rf $ncdir_copy && cp -r -T $ncdir/. $ncdir_copy && mkdir -p $n1dir));

        print("copying $ncdir contents to $n1dir\n");
        # Copy $ncdir () to $n1dir
        run_command_and_exit_iferr(qq(cp -r $ncdir_copy/* $n1dir/));
=======
    # Create $n1dir with -p switch
    print("Creating $n1dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n1dir));

    # Check if $ncdir exists
    if (-e $ncdir) {
        print("$ncdir already exists, copying its concents to $n1dir\n");
        # Copy everything under $ncdir to $n1dir
        run_command_and_exit_iferr(qq(cp -r $ncdir/* $n1dir/));
>>>>>>> REL24_1

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
<<<<<<< HEAD
    # Create $n1dir with -p switch
    print("Creating $n1dir\n");
    run_command_and_exit_iferr(qq(mkdir -p $n1dir));

=======
>>>>>>> REL24_1
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











=pod
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

my $n1dir="$ENV{EDGE_CLUSTER_DIR}/n1";
my $homedir1="$n1dir/pgedge";

print("whoami = $ENV{EDGE_REPUSER}\n");

# First, we create a directory to hold node 1. 

my $cmd = qq(mkdir -p $n1dir);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#print("success = $success\n");
print("full_buf = @$full_buf\n");
#print("stderr_buf = @$stderr_buf\n");

# Download the install.py file into the directory

my $cmd2 = qq(curl -fsSL $ENV{EDGE_REPO} > $n1dir/install.py);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("success2 = $success2\n");
#print("full_buf2 = @$full_buf2\n");
#print("stderr_buf2 = @$stderr_buf2\n");


# Move into the pgedge directory and run the install.py file.

chdir("./$n1dir");

my $cmd3 = qq(python install.py);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

#print("success3 = $success3\n");
#print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");

chdir("./../../../../");
# Install PostgreSQL.

my $cmd4 = qq($homedir1/$ENV{EDGE_CLI} install pgedge -U $ENV{EDGE_USERNAME} -P $ENV{EDGE_PASSWORD} -d $ENV{EDGE_DB} -p $ENV{EDGE_START_PORT} --pg $ENV{EDGE_INST_VERSION});
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

#print("success4 = $success4\n");
print("full_buf4 = @$full_buf4\n");
#print("stderr_buf4 = @$stderr_buf4\n");
# In this case, stdout_buf4 contains content

print("The home directory is $homedir1\n");

print("The port number is $ENV{EDGE_START_PORT}\n");

# Then, use the info to connect to psql and test for the existence of the extension.

my $cmd5 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM pg_available_extensions WHERE name='spock'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

#print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

# Test to confirm that cluster is set up.

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");
print("full_buf5 = @$full_buf5\n");
print("We just installed pgedge/spock in $n1dir.\n");

=head
foreach (sort keys %ENV) {
#    where ENV contains EDGE_ - look for selecting a regex from Env
    next if $_ !~ "^EDGE_*";
    print "$_  =  $ENV{$_}\n";
}
=cut
=pod
if(contains(@$stdout_buf5[0], "spock"))

{
    exit(0);
}
else
{
    exit(1);
}

=cut


