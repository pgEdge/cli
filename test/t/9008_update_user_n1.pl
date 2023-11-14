# In this test case, we assign a password to the role specified in username and add the name to the 
# ./pgpass file.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

our $repuser = `whoami`;
our $username = "$ENV{EDGE_USERNAME}";
our $password = "$ENV{EDGE_PASSWORD}";
our $database = "$ENV{EDGE_DB}";
our $inst_version = "$ENV{EDGE_INST_VERSION}";
our $cmd_version = "$ENV{EDGE_COMPONENT}";
our $spock = "$ENV{EDGE_SPOCK}";
our $cluster = "$ENV{EDGE_CLUSTER}";
our $repset = "$ENV{EDGE_REPSET}";
our $n1 = "$ENV{EDGE_N1}";
our $n2 = "$ENV{EDGE_N2}";
our $n3 = "$ENV{EDGE_N3}";

# We can retrieve the home directory from nodectl in json form... 

my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n"); 

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $cmd_version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number is {$port}\n");

# Then, we add an entry to the ~/.pgpass file for the user.

my $cmd10 = qq(echo "*:*:*:$repuser:$password" >> ~/.pgpass);
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);
print("$cmd10 adds the password to the pgpass file.\n");

# Then, we connect with psql and confirm that the user exists and has a password.

my $cmd7 = qq($homedir/$cmd_version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "ALTER ROLE $repuser LOGIN PASSWORD '$password'");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

# Then, confirm that the role has been altered.

print("We just altered $username to add a password ($password).\n");

if(contains(@$stdout_buf7[0], "ALTER ROLE"))

{
    exit(0);
}
else
{
    exit(1);
}

