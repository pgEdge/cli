# In this test case, we create the table for node 1.
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
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# Node 1:
# We can retrieve the home directory from nodectl in json form...
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Create table on Node 1:

my $cmd6 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "CREATE TABLE foo (col1 INT PRIMARY KEY)");
print("cmd6 = $cmd6\n");
my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
print("stdout_buf6= @$stdout_buf6\n");

my $cmd9 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.tables");
print("cmd9 = $cmd9\n");
my ($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
print("stdout_buf9= @$stdout_buf9\n");

# Inserting into public.foo table

my $cmd7 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "INSERT INTO foo select generate_series(1,10)");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
print("stdout_buf7= @$stdout_buf7\n");

#Adding Table to the Repset

my $cmd8 = qq($homedir/nodectl spock repset-add-table $repset foo $database);
print("cmd8 = $cmd8\n");
my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
print("stdout_buf8 = @$stdout_buf8\n");

# Then, we connect with psql and confirm that a table named foo exists.

my $cmd17 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM foo");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);
print("stdout_buf17 = @$stdout_buf17\n");

print("We just created the table on ($n1) and are now verifying it exists.\n");

if(contains(@$stdout_buf17[0], "10"))

{
    exit(0);
}
else
{
    exit(1);
}
