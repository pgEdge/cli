# This test case will install pgedge in node1 (n1) and validate it exists.

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
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $snowflakeversion = "snowflake-$pgversion";
my $spver = $ENV{EDGE_SPOCK} =~ s/\.//r; #removing the . from version so that 3.2 becomes 32
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16
my $exitcode = 0;

# Install pgedge
print("Install pgedge\n");
chdir("./$homedir1");
my $out_buf = (run_command_and_exit_iferr(qq(./$cli setup -U $ENV{EDGE_USERNAME} -P $ENV{EDGE_PASSWORD} -d $ENV{EDGE_DB} -p $ENV{EDGE_START_PORT} --pg_ver $ENV{EDGE_INST_VERSION})))[3];

# Check if 'already installed' is present in stdout_buf
if (grep { /already installed/i } @$out_buf) {
    print("pgedge already installed, Exiting. Full Buffer (Install): @$out_buf\n");
    $exitcode = 0;
}

#check for pgV
my $cmd = qq(./$cli um list);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success) && !is_umlist_component_installed($stdout_buf, "$pgversion")) 
{
    print("cmd = $cmd\n");
    $exitcode=1;
} 

#check for spock
my $cmd2 = qq(./$cli um list);
print("cmd = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success2) && !is_umlist_component_installed($stdout_buf2, "$spockversion")) 
{
    $exitcode=1;
} 

#check for snowflake
my $cmd3 = qq(./$cli um list);
print("cmd = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success3) && !is_umlist_component_installed($stdout_buf3, "$snowflakeversion")) 
{
    $exitcode=1;
} 


# Set the exitcode based on component installations
exit($exitcode);