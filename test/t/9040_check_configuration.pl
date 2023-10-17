# This test case updates a record on node 1 that should then be written to node 2 
# in test case 915.

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

# We can retrieve the home directory from nodectl in json form... 
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

# We can retrieve the home directory from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory is {$homedir2}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n1/pgedge/nc --json info pg16`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number is {$port2}\n");


# Use psql to check the setup:
#

my $cmd25 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.node");
print("cmd25 = $cmd25\n");
my($success25, $error_message25, $full_buf25, $stdout_buf25, $stderr_buf25)= IPC::Cmd::run(command => $cmd25, verbose => 0);
print("stdout_buf25 = @$stdout_buf25\n");

my $cmd26 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription");
print("cmd26 = $cmd26\n");
my($success26, $error_message26, $full_buf26, $stdout_buf26, $stderr_buf26)= IPC::Cmd::run(command => $cmd26, verbose => 0);
print("stdout_buf26 = @$stdout_buf26\n");

my $cmd27 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.tables");
print("cmd27 = $cmd27\n");
my($success27, $error_message27, $full_buf27, $stdout_buf27, $stderr_buf27)= IPC::Cmd::run(command => $cmd27, verbose => 0);
print("stdout_buf27 = @$stdout_buf27\n");

my $cmd28 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);

# On Node 2:
# Use psql to check the setup:

my $cmd35 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM spock.node");
print("cmd35 = $cmd35\n");
my($success35, $error_message35, $full_buf35, $stdout_buf35, $stderr_buf35)= IPC::Cmd::run(command => $cmd35, verbose => 0);
print("stdout_buf35 = @$stdout_buf35\n");

my $cmd36 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription");
print("cmd36 = $cmd36\n");
my($success36, $error_message36, $full_buf36, $stdout_buf36, $stderr_buf36)= IPC::Cmd::run(command => $cmd36, verbose => 0);
print("stdout_buf36 = @$stdout_buf36\n");

my $cmd37 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.tables");
print("cmd37 = $cmd37\n");
my($success37, $error_message37, $full_buf37, $stdout_buf37, $stderr_buf37)= IPC::Cmd::run(command => $cmd37, verbose => 0);
print("stdout_buf37 = @$stdout_buf37\n");

my $cmd38 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd38 = $cmd38\n");
my($success38, $error_message38, $full_buf38, $stdout_buf38, $stderr_buf38)= IPC::Cmd::run(command => $cmd38, verbose => 0);
print("stdout_buf38 = @$stdout_buf38\n");

# Now, confirm that the update on ($n1) took place:

if(contains(@$stdout_buf28[0], "demo-repset"))

{
    exit(0);
}
else
{
    exit(1);

}


