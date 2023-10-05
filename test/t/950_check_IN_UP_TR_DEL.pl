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

# Use psql to check that default values for INSERT, UPDATE, DELETE, and TRUNCATE work as expected....
#

my $cmd25 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "INSERT INTO pgbench_tellers VALUES (15, 16, 17.00, 'INSERT statement')");
print("cmd25 = $cmd25\n");
my($success25, $error_message25, $full_buf25, $stdout_buf25, $stderr_buf25)= IPC::Cmd::run(command => $cmd25, verbose => 0);
print("stdout_buf25 = @$stdout_buf25\n");

if(!(contains(@$stdout_buf25[0], "INSERT")))

{
    exit(1);
}

my $cmd26 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "UPDATE pgbench_tellers SET filler='UPDATE statement' WHERE tid = 15");
print("cmd26 = $cmd26\n");
my($success26, $error_message26, $full_buf26, $stdout_buf26, $stderr_buf26)= IPC::Cmd::run(command => $cmd26, verbose => 0);
print("stdout_buf26 = @$stdout_buf26\n");

if(!(contains(@$stdout_buf26[0], "UPDATE")))

{
    exit(1);
}

my $cmd27 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "DELETE FROM pgbench_tellers WHERE tid = 15");
#print("cmd27 = $cmd27\n");
my($success27, $error_message27, $full_buf27, $stdout_buf27, $stderr_buf27)= IPC::Cmd::run(command => $cmd27, verbose => 0);
print("stdout_buf27 = @$stdout_buf27\n");

if(!(contains(@$stdout_buf27[0], "DELETE")))

{
    exit(1);
}

my $cmd28 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "TRUNCATE pgbench_tellers");
#print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);

if((contains(@$stdout_buf28[0], "TRUNCATE")))

{
    exit(0);
}
{
    exit(1);
}


