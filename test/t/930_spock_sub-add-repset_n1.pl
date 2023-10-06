# In this test case, we add the replication set to the subscription on node 1.
#

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# On node 1:
# We can retrieve the home directory from nodectl in json form...
#
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Confirm that the spock sub-add-repset command fails gracefully if the subscription name is omitted:

my $cmd2 = qq($homedir/nodectl spock sub-add-repset $repset $database);
print("cmd2 = $cmd2\n");
my($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

if(!(contains(@$stderr_buf2[0], "ERROR")))
{
    exit(1);
}

# Confirm that the spock sub-add-repset command fails gracefully if the repset name is omitted:

my $cmd3 = qq($homedir/nodectl spock sub-add-repset sub_n1n2 $database);
print("cmd3 = $cmd3\n");
my($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

if(!(contains(@$stderr_buf3[0], "ERROR")))
{
    exit(1);
}

# Confirm that the spock sub-add-repset command fails gracefully if the database name is omitted:

my $cmd4 = qq($homedir/nodectl spock sub-add-repset sub_n1n2 $repset);
print("cmd4 = $cmd4\n");
my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

if(!(contains(@$stderr_buf4[0], "ERROR")))
{
    exit(1);
}

# Then, add the repset to the subscription on node 1:

my $cmd23 = qq($homedir/nodectl spock sub-add-repset sub_n1n2 $repset $database);
print("cmd23 = $cmd23\n");
my($success23, $error_message23, $full_buf23, $stdout_buf23, $stderr_buf23)= IPC::Cmd::run(command => $cmd23, verbose => 0);

print("We just added the replication set to the subscription on ($n1) to connect to ($n2).\n");

my $cmd20 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.subscription");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
print("stdout_buf20 = (@$stdout_buf20)\n");

if(contains(@$stdout_buf20[0], "sub_n1n2"))

{
    exit(0);
}
else
{
    exit(1);

}



