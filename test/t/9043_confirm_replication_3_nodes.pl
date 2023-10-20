# This test case confirms that the row updated in test t/914 is correctly 
# replicated on node 2.

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
my $n3 = "~/work/nodectl/test/pgedge/cluster/demo/n3";


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
my $json4 = `$n2/pgedge/nc --json info pg16`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number is {$port2}\n");

# We can retrieve the home directory from nodectl in json form... 
my $json5 = `$n3/pgedge/nc --json info`;
#print("my json = $json5");
my $out5 = decode_json($json5);
my $homedir3 = $out5->[0]->{"home"};
print("The home directory is {$homedir3}\n");

# We can retrieve the port number from nodectl in json form...
my $json6 = `$n3/pgedge/nc --json info pg16`;
#print("my json = $json6");
my $out6 = decode_json($json6);
my $port3 = $out6->[0]->{"port"};
print("The port number is {$port3}\n");

# Connect to psql on node 1 and add a record to the 'pgbench_tellers' table:

my $cmd28 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "INSERT INTO pgbench_tellers VALUES (78, 79, 80, 'On-your-mark')");
print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);
# print("stdout_buf = @$stdout_buf28\n");
print("We've just added a row to the foo table on $n1 using $port\n");

# Test to see if replication is working on node 2:

my $cmd29 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);
# print("stdout_buf = @$stdout_buf29\n");

# Test for the search_term in a buffer.

if (!(contains(@$stdout_buf29[0], "On-your-mark")))
{
    exit(1);
}

# Test to see if replication is working to node 3:

my $cmd27 = qq($homedir3/$version/bin/psql -t -h 127.0.0.1 -p $port3 -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd27 = $cmd27\n");
my($success27, $error_message27, $full_buf27, $stdout_buf27, $stderr_buf27)= IPC::Cmd::run(command => $cmd27, verbose => 0);
# print("stdout_buf = @$stdout_buf27\n");

# Test for the search_term in a buffer.

if (!(contains(@$stdout_buf27[0], "On-your-mark")))
{
    exit(1);
}

# Connect to psql on node 2 and add a record to the 'pgbench_tellers' table:

my $cmd38 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "INSERT INTO pgbench_tellers VALUES (81, 82, 83, 'Get-set')");
print("cmd38 = $cmd38\n");
my($success38, $error_message38, $full_buf38, $stdout_buf38, $stderr_buf38)= IPC::Cmd::run(command => $cmd38, verbose => 0);
# print("stdout_buf = @$stdout_buf38\n");
print("We've just added a row to the foo table on $n2 using $port2\n");

# Test to see if replication is working on node 1:

my $cmd39 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd39 = $cmd39\n");
my($success39, $error_message39, $full_buf39, $stdout_buf39, $stderr_buf39)= IPC::Cmd::run(command => $cmd39, verbose => 0);
# print("stdout_buf = @$stdout_buf39\n");

# Test for the search_term in a buffer.

if (!(contains(@$stdout_buf39[0], "Get-set")))
{
    exit(1);
}

# Test to see if replication is working to node 3:

my $cmd37 = qq($homedir3/$version/bin/psql -t -h 127.0.0.1 -p $port3 -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd37 = $cmd37\n");
my($success37, $error_message37, $full_buf37, $stdout_buf37, $stderr_buf37)= IPC::Cmd::run(command => $cmd37, verbose => 0);
# print("stdout_buf = @$stdout_buf37\n");

# Test for the search_term in a buffer.

if (!(contains(@$stdout_buf37[0], "Get-set")))
{
    exit(1);
}

# Connect to psql on node 3 and add a record to the 'pgbench_tellers' table:

my $cmd48 = qq($homedir3/$version/bin/psql -t -h 127.0.0.1 -p $port3 -d $database -c "INSERT INTO pgbench_tellers VALUES (84, 85, 86, 'GO!')");
print("cmd48 = $cmd48\n");
my($success48, $error_message48, $full_buf48, $stdout_buf48, $stderr_buf48)= IPC::Cmd::run(command => $cmd48, verbose => 0);
# print("stdout_buf = @$stdout_buf48\n");
print("We've just added a row to the foo table on $n3 using $port3\n");

# Test to see if replication is working on node 1:

my $cmd49 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd49 = $cmd49\n");
my($success49, $error_message49, $full_buf49, $stdout_buf49, $stderr_buf49)= IPC::Cmd::run(command => $cmd49, verbose => 0);
# print("stdout_buf = @$stdout_buf49\n");

# Test for the search_term in a buffer.

if (!(contains(@$stdout_buf49[0], "GO!")))
{
    exit(1);
}

# Test to see if replication is working to node 2:

my $cmd47 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM pgbench_tellers");
print("cmd47 = $cmd47\n");
my($success47, $error_message47, $full_buf47, $stdout_buf47, $stderr_buf47)= IPC::Cmd::run(command => $cmd47, verbose => 0);
# print("stdout_buf = @$stdout_buf47\n");

# Test for the search_term in a buffer.

if (contains(@$stdout_buf47[0], "GO!"))
{
    exit(0);
}
else
{
    exit(1);
}

