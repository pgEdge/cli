# This test case will create the second of a two-node cluster.
# 

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

my $n2dir="$ENV{EDGE_CLUSTER_DIR}/n2";
my $homedir2="$n2dir/pgedge";
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;

print("whoami = $ENV{EDGE_REPUSER}\n");

# First, we create a directory to hold node 1. 

my $cmd = qq(mkdir -p $n2dir);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#print("success = $success\n");
print("full_buf = @$full_buf\n");
#print("stderr_buf = @$stderr_buf\n");

# Download the install.py file into the directory

my $cmd2 = qq(curl -fsSL $ENV{EDGE_REPO} > $n2dir/install.py);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("success2 = $success2\n");
#print("full_buf2 = @$full_buf2\n");
#print("stderr_buf2 = @$stderr_buf2\n");


# Move into the pgedge directory and run the install.py file.

chdir("./$n2dir");

my $cmd3 = qq(python install.py);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

#print("success3 = $success3\n");
#print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");

chdir("./../../../../");
# Install PostgreSQL.

my $cmd4 = qq($homedir2/$ENV{EDGE_CLI} install pgedge -U $ENV{EDGE_USERNAME} -P $ENV{EDGE_PASSWORD} -d $ENV{EDGE_DB} -p $myport2 --pg $ENV{EDGE_INST_VERSION});
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

#print("success4 = $success4\n");
print("full_buf4 = @$full_buf4\n");
#print("stderr_buf4 = @$stderr_buf4\n");
# In this case, stdout_buf4 contains content

print("The home directory is $homedir2\n");

print("The port number is $myport2\n");

# Then, use the info to connect to psql and test for the existence of the extension.

my $cmd5 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM pg_available_extensions WHERE name='spock'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

#print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

# Test to confirm that cluster is set up.

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");
print("full_buf5 = @$full_buf5\n");
print("We just installed pgedge/spock in $n2dir.\n");

=head
foreach (sort keys %ENV) {
#    where ENV contains EDGE_ - look for selecting a regex from Env
    next if $_ !~ "^EDGE_*";
    print "$_  =  $ENV{$_}\n";
}
=cut

if(contains(@$stdout_buf5[0], "spock"))

{
    exit(0);
}
else
{
    exit(1);
}
