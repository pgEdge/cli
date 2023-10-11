# This case tests spock repset-add-table, repset-remove-table, and repset-drop.
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

my $cmd99 = qq(whoami);
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
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
# print("The port number is {$port}\n");

# Register node 1 and the repset entry on n1: 
print("repuser before chomp = $repuser\n");
chomp($repuser);

# Connect to psql and test for the existence of my_new_repset.

my $cmd33 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd33 = $cmd33\n");
my($success33, $error_message33, $full_buf33, $stdout_buf33, $stderr_buf33)= IPC::Cmd::run(command => $cmd33, verbose => 0);

if(!(contains(@$stdout_buf33[0], "my_new_repset       | t                | t                | t                | t")))
{
    # If it doesn't exist, create my_new_repset:

    my $cmd31 = qq($homedir/nodectl spock repset-create my_new_repset lcdb);
    print("cmd31 = $cmd31\n");
    my ($success31, $error_message31, $full_buf31, $stdout_buf31, $stderr_buf31)= IPC::Cmd::run(command => $cmd31, verbose => 0);
}

# Then, connect to psql and create a table:

my $cmd42 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "CREATE TABLE newfoo (name VARCHAR(40), amount INTEGER, pkey INTEGER PRIMARY KEY)");
print("cmd42 = $cmd42\n");
my($success42, $error_message42, $full_buf42, $stdout_buf42, $stderr_buf42)= IPC::Cmd::run(command => $cmd42, verbose => 0);

if(!(contains(@$full_buf42[0], "CREATE TABLE")))

{
    exit(1);
}

# Invoke: ./nc spock repset-add-table to add the table to the repset.

my $cmd44 = qq($homedir/nodectl spock repset-add-table my_new_repset newfoo lcdb);
print("cmd44 = $cmd44\n");
my ($success44, $error_message44, $full_buf44, $stdout_buf44, $stderr_buf44)= IPC::Cmd::run(command => $cmd44, verbose => 0);

# We need to use psql to check the result for certain:

my $cmd45 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set_table");
print("cmd45 = $cmd45\n");
my($success45, $error_message45, $full_buf45, $stdout_buf45, $stderr_buf45)= IPC::Cmd::run(command => $cmd45, verbose => 0);

if(!(contains(@$stdout_buf45[0], "newfoo")))
{
    exit(1);
}

# Invoke: ./nc spock repset-remove-table to remove the table from the repset.

my $cmd48 = qq($homedir/nodectl spock repset-remove-table my_new_repset newfoo lcdb);
print("cmd48 = $cmd48\n");
my ($success48, $error_message48, $full_buf48, $stdout_buf48, $stderr_buf48)= IPC::Cmd::run(command => $cmd48, verbose => 0);

# We need to use psql to check the result for certain:

my $cmd49 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set_table");
print("cmd49 = $cmd49\n");
my($success49, $error_message49, $full_buf49, $stdout_buf49, $stderr_buf49)= IPC::Cmd::run(command => $cmd49, verbose => 0);

if(contains(@$stdout_buf49[0], "newfoo"))
{
    exit(1);
}

# Invoke: ./nc spock repset-drop to remove our repset:

my $cmd46 = qq($homedir/nodectl spock repset-drop my_new_repset lcdb);
print("cmd46 = $cmd46\n");
my ($success46, $error_message46, $full_buf46, $stdout_buf46, $stderr_buf46)= IPC::Cmd::run(command => $cmd46, verbose => 0);

# We need to use psql to check for the repset; if it's not there, our test passes:

my $cmd47 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd47 = $cmd47\n");
my($success47, $error_message47, $full_buf47, $stdout_buf47, $stderr_buf47)= IPC::Cmd::run(command => $cmd47, verbose => 0);

if(!(contains(@$full_buf47[0], "{my_new_repset}")))
{
    exit(0);
}
else
{
    exit(1);
}





