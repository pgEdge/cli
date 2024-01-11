# 020_nodectl_install_pg.pl
# This script does the initial setup for um related tests in the 300 series. It checks if the $n1dir already
# exists, then it assumes both curl and install script has been executed. 

# TODO : The $n1dir check is probably not enough,  we need to check for more objects 
# At present the 300 series tests are using the same directory structure as used by the 
# 8000 series tests for n1. This will be changed to use different directory that will be 
# common for other tests (e.g. service, app, cluster etc)

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

sub handle_error_and_exit {
    my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf) = @_;

    if (!$success) {
        print "Error: $error_message\n";
        print "Full Buffer: @{$full_buf}";
        #print "Stdout Buffer: @{$stdout_buf}";
        #print "Stderr Buffer: @{$stderr_buf}";
        exit(1);
    }
}

my $n1dir = "$ENV{EDGE_CLUSTER_DIR}/n1";
my $homedir1 = "$n1dir/pgedge";

print "whoami = $ENV{EDGE_REPUSER}\n";

# Check if the directory already exists
if (-e $homedir1) {
    print "$homedir1 already installed...\n skipping the download and install and exiting with success\n";
    exit(0);
}

# Create a directory to hold a node.
my $cmd = qq(mkdir -p $n1dir);
print "Executing cmd = $cmd\n";
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf) = IPC::Cmd::run(command => $cmd, verbose => 0);
handle_error_and_exit($success, $error_message, $full_buf, $stdout_buf, $stderr_buf);

# Download the install.py file into the directory
my $cmd2 = qq(curl -fsSL $ENV{EDGE_REPO} > $n1dir/install.py);
print "Executing cmd2 = $cmd2\n";
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2) = IPC::Cmd::run(command => $cmd2, verbose => 0);
handle_error_and_exit($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2);

chdir("./$n1dir");

# Run the install.py file.
my $cmd3 = qq(python install.py);
print "Executing cmd3 = $cmd3\n";
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3) = IPC::Cmd::run(command => $cmd3, verbose => 0);
handle_error_and_exit($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3);

chdir("./../../../../");

# Success
exit(0);
