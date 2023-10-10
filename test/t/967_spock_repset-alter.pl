# This case tests spock repset-alter.
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


# Create a new replication set to modify:

my $cmd31 = qq($homedir/nodectl spock repset-create my_new_repset lcdb);
print("cmd31 = $cmd31\n");
my ($success31, $error_message31, $full_buf31, $stdout_buf31, $stderr_buf31)= IPC::Cmd::run(command => $cmd31, verbose => 0);

if(!(contains(@$stdout_buf31[0], "repset_create")))
{
    exit(1);
}

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd33 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd33 = $cmd33\n");
my($success33, $error_message33, $full_buf33, $stdout_buf33, $stderr_buf33)= IPC::Cmd::run(command => $cmd33, verbose => 0);

if(!(contains(@$stdout_buf33[0], "my_new_repset       | t                | t                | t                | t")))
{
    exit(1);
}

# We'll leave off the database name to check the error with the repset-alter command...

my $cmd32 = qq($homedir/nodectl spock repset-alter my_new_repset);
print("cmd32 = $cmd32\n");
my ($success32, $error_message32, $full_buf32, $stdout_buf32, $stderr_buf32)= IPC::Cmd::run(command => $cmd32, verbose => 0);

if(!(contains(@$stderr_buf32[0], "ERROR")))
{
    exit(1);
}

# We'll alter the repset now, so it doesn't accept INSERT statements...

my $cmd34 = qq($homedir/nodectl spock repset-alter my_new_repset lcdb --replicate_delete=false);
print("cmd34 = $cmd34\n");
my ($success34, $error_message34, $full_buf34, $stdout_buf34, $stderr_buf34)= IPC::Cmd::run(command => $cmd34, verbose => 0);

if(!(contains(@$full_buf34[0], "repset_alter")))
{
    exit(1);
}


# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd5 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

if(contains(@$stdout_buf5[0], "my_new_repset       | t                | t                | f                | t"))

{
    exit(0);
}
else
{
    exit(1);
}





