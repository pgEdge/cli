# This test case will create the first of a two-node cluster.
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

print("whoami = $ENV{EDGE_REPUSER}\n");

# First, we create a directory to hold node 2. 



my $cmd = qq(mkdir -p $ENV{EDGE_N2});
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#print("success = $success\n");
print("full_buf = @$full_buf\n");
#print("stderr_buf = @$stderr_buf\n");

# Download the install.py file into the directory

my $cmd2 = qq(curl -fsSL $ENV{EDGE_REPO} > $ENV{EDGE_N2}/install.py);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("success2 = $success2\n");
#print("full_buf2 = @$full_buf2\n");
#print("stderr_buf2 = @$stderr_buf2\n");


# Move into the pgedge directory and run the install.py file.

chdir("./$ENV{EDGE_CHDIR2}");

my $cmd3 = qq(python $ENV{EDGE_N2}/install.py);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("success3 = $success3\n");
print("full_buf3 = @$full_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");


# Install PostgreSQL.

my $cmd4 = qq($ENV{EDGE_N2}/pgedge/nodectl install pgedge -U $ENV{EDGE_USERNAME} -P $ENV{EDGE_PASSWORD} -d $ENV{EDGE_DB} -p $ENV{EDGE_PORT2});
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

#print("success4 = $success4\n");
print("full_buf4 = @$full_buf4\n");
#print("stderr_buf4 = @$stderr_buf4\n");
# In this case, stdout_buf4 contains content

# Confirm that the node is installed properly - retrieve the path and port:

my $json = `$ENV{EDGE_N2}/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
$ENV{EDGE_HOMEDIR2} = $out->[0]->{"home"};

print("The home directory is {$ENV{EDGE_N2}}\n");

my $json2 = `$ENV{EDGE_N2}/pgedge/nc --json info $ENV{EDGE_VERSION}`;
#print("my json2 = $json2");
my $out2 = decode_json($json2);
$ENV{EDGE_PORT2} = $out2->[0]->{"port"};

print("The port number is $ENV{EDGE_PORT2}\n");

# Then, use the info to connect to psql and test for the existence of the extension.

my $cmd5 = qq($ENV{EDGE_HOMEDIR2}/$ENV{EDGE_VERSION}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_PORT2} -d $ENV{EDGE_DB} -c "SELECT * FROM pg_available_extensions WHERE name='spock'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

#print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

# Test to confirm that cluster is set up.

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");
print("full_buf5 = @$full_buf5\n");
print("We just installed pgedge/spock in $ENV{EDGE_N2}.\n");

if(contains(@$stdout_buf5[0], "3.2"))

{
    exit(0);
}
else
{
    exit(1);
}



