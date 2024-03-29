# This test case will the second of a two-node cluster with the nodectl install pgedge command.
# You should run case 920_ right before this case to create node 1.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

my $cmd99 = qq(whoami);
print("cmd99 = $cmd99\n");
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $inst_version = "--pg 17";
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";
my $n3 = "~/work/nodectl/test/pgedge/cluster/demo/n3";

# First, we create a directory to hold node 3. 

my $cmd = qq(mkdir -p $n3);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");

# Download the install.py file into the directory.

my $cmd2 = qq(curl -fsSL https://pgedge-upstream.s3.amazonaws.com/REPO/install24.py > $n3/install.py);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("full_buf2 = @$full_buf2\n");

# Move into the pgedge directory and run the install.py file.

chdir("./pgedge/cluster/demo/n3/");

print("We just moved into $n3");

my $cmd3 = qq(python $n3/install.py);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("full_buf3 = @$full_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");

# Install PostgreSQL.

my $cmd4 = qq($n3/pgedge/nodectl install pgedge -U $username -P $password -d $database -p 6434 $inst_version);
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("full_buf4 = @$full_buf4\n");
print("stderr_buf4 = @$stderr_buf4\n");

# Confirm that the node is installed properly - retrieve the path and port:

my $json = `$n3/pgedge/nc --json info`;
print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};

print("The home directory is {$homedir}\n");

my $json2 = `$n3/pgedge/nc --json info pg17`;
print("my json2 = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};

print("The port number is {$port}\n");

# Then, use the info to connect to psql and test for the existence of the extension.

my $cmd5 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pg_available_extensions WHERE name='spock'");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("success5 = $success5\n");
print("stdout_buf5 = @$stdout_buf5\n");

# Test to confirm that cluster is set up.

print("stdout_buf5 = @$stdout_buf5\n");
print("We just installed pgedge/spock in $n1.\n");

if(contains(@$stdout_buf5[0], "$spock"))

{
    exit(0);
}
else
{
    exit(1);
}

