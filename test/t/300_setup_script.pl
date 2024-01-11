#
# This test sets up a database cluster, adds the user to the pgpass file, and checks for the installed status
# This test does a multi step pgV install through the install, init and start
#

use strict;
use warnings;
use File::Which;
use Try::Tiny;
use IPC::Cmd qw(run);
use JSON;
use lib './t/lib';
use contains;

# Define a subroutine to run a command and handle errors
sub run_command {
    my ($cmd) = @_;
    print ("Executing : $cmd\n");
    my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf) = IPC::Cmd::run(command => $cmd, verbose => 0);

    if (!defined($success)) {
        print("Error executing command $cmd: $error_message\n");
        print("Full Buffer output : @$full_buf\n");
        exit(1);
    }

    return ($success, $full_buf, $stdout_buf, $stderr_buf);
}

# Our parameters are:

my $username = $ENV{EDGE_USERNAME};
my $password = $ENV{EDGE_PASSWORD};
my $database = $ENV{EDGE_DB};
my $port = $ENV{EDGE_START_PORT};
my $pgversion = $ENV{EDGE_COMPONENT};
my $homedir="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $cli = $ENV{EDGE_CLI};
my $exitcode = 0;
#my $spock = "3.1";

# Doing a multi step pgV install on a custom port 
# um install pgV
my ($success, $full_buf, $stdout_buf, $stderr_buf) = run_command(qq($homedir/$cli um install $pgversion));
# Check if 'already installed' is present in stdout_buf
if (grep { /already installed/i } @$stdout_buf) {
    print("$pgversion Already installed, Exiting. Full Buffer (Install): @$stdout_buf\n");
    exit(1);
}

# initialise cluster (initdb) through init pgV specifying a custom port
run_command(qq(pgePasswd=$password $homedir/$cli init $pgversion --port=$port));

# Starting pgV server
run_command(qq($homedir/$cli start $pgversion));

print("Adding credentials to .pgpass file");
run_command(qq(echo "*:*:*:$username:$password" >> ~/.pgpass && chmod 600 ~/.pgpass));

my $cmd2 = qq($homedir/$cli um list);
print("cmd = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success2)) 
{
    if (!(is_umlist_component_installed($stdout_buf2, $pgversion)))
    {
        print("$pgversion not installed. Setting exit code to 1\n");
        $exitcode = 1;
    }
} 
else
{
    print("$cmd2 not executed successfully. Full buffer: @$full_buf2\n");
    $exitcode = 1;
}

exit($exitcode);
