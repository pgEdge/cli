# In this case, we create the subscription on node 2 with nc spock sub-create.
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

print("repuser before chomp = $repuser\n");
chomp($repuser);

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir1 = $out->[0]->{"home"};
print("The home directory is {$homedir1}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port1 = $out2->[0]->{"port"};
print("The port number is {$port1}\n");

# We can retrieve the home directory from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory is {$homedir2}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
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
my $json6 = `$n3/pgedge/nc --json info $version`;
#print("my json = $json6");
my $out6 = decode_json($json6);
my $port3 = $out6->[0]->{"port"};
print("The port number is {$port3}\n");

# Create the subscription between node 2 and node 1:

my $cmd12 = qq($homedir2/nodectl spock sub-create sub_n2n1 'host=127.0.0.1 port=$port1 user=$repuser dbname=$database' $database);
print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
print("stdout_buf12 = @$stdout_buf12\n");

# Then, we connect with psql:

my $cmd17 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM spock.subscription");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);

# Then, confirm that the subscription has been created.

print("We just created the subscription on ($n2) and are now verifying it exists.\n");
if(!(contains(@$stdout_buf17[0], "sub_n2n1")))
{
    exit(1);
}

# Create the subscription between node 2 and node 3:

my $cmd13 = qq($homedir2/nodectl spock sub-create sub_n2n3 'host=127.0.0.1 port=$port3 user=$repuser dbname=$database' $database);
print("cmd13 = $cmd13\n");
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
print("stdout_buf13 = @$stdout_buf13\n");

# Then, we connect with psql:

my $cmd7 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM spock.subscription");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

# Then, confirm that the subscription has been created.

print("We just created the subscription with ($n3) on ($n2) and are now verifying it exists.\n");
if(!(contains(@$stdout_buf7[0], "sub_n2n3")))
{
    exit(1);
}
else
{
    exit(0);
}


