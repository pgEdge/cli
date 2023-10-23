# In this step, we create the subscription on node 3.

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
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";
my $n3 = "~/work/nodectl/test/pgedge/cluster/demo/n3";

# We can retrieve the home directory for node 1 from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
print("The home directory of node 1 is {$homedir1}\n");

# We can retrieve the port number for node 1 from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $version`;
# print("my json = $json2");
my $out2 = decode_json($json2);
my $port1 = $out2->[0]->{"port"};
print("The port number on node 1 is {$port1}\n");

# We can retrieve the home directory for node 2 from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
# print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory of node 2 is {$homedir2}\n");

# We can retrieve the port number for node 2 from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
# print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number of node 2 is {$port2}\n");

# We can retrieve the home directory from nodectl in json form... 
my $json5 = `$n3/pgedge/nc --json info`;
#print("my json = $json5");
my $out5 = decode_json($json5);
my $homedir3 = $out5->[0]->{"home"};
print("The home directory of node 3 is {$homedir3}\n");

# We can retrieve the port number from nodectl in json form...
my $json6 = `$n3/pgedge/nc --json info $version`;
#print("my json = $json6");
my $out6 = decode_json($json6);
my $port3 = $out6->[0]->{"port"};
print("The port number of node 3 is {$port3}\n");

print("repuser before chomp = $repuser\n");
chomp($repuser);

# Create the subscription on n3 to node 1:

my $cmd11 = qq($homedir3/nodectl spock sub-create sub_n3n1 'host=127.0.0.1 port=$port1 user=$repuser dbname=$database' $database);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
print("stdout_buf11 = @$stdout_buf11\n");

# Then, we connect with psql:

my $cmd7 = qq($homedir3/$version/bin/psql -t -h 127.0.0.1 -p $port3 -d $database -c "SELECT * FROM spock.subscription");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

# Then, confirm that the subscription exists:

print("We just created the subscription with ($n1) on ($n3) and are now verifying it exists.\n");

if(!(contains(@$stdout_buf7[0], "sub_n3n1")))
    
{   
    exit(1);
}   

# Create the subscription from n3 to node 2:

my $cmd14 = qq($homedir3/nodectl spock sub-create sub_n3n2 'host=127.0.0.1 port=$port2 user=$repuser dbname=$database' $database);
print("cmd14 = $cmd14\n");
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
print("stdout_buf14 = @$stdout_buf14\n");

# Then, we connect with psql:

my $cmd17 = qq($homedir3/$version/bin/psql -t -h 127.0.0.1 -p $port3 -d $database -c "SELECT * FROM spock.subscription");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);

# Then, confirm that the subscription exists:

print("We just created the subscription with ($n2) on ($n3) and are now verifying it exists.\n");

if(contains(@$stdout_buf17[0], "sub_n3n2"))

{
    exit(0);
}
else
{
    exit(1);
}

