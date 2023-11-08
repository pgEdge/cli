# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this step, we drop the subscription on node 1.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
# Our parameters are:


print("whoami = $ENV{EDGE_REPUSER}\n");

# We can retrieve the home directory for node 1 from nodectl in json form... 

my $json = `$ENV{EDGE_N1}/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
$ENV{EDGE_HOMEDIR1} = $out->[0]->{"home"};
print("The home directory of node 1 is {$ENV{EDGE_HOMEDIR1}}\n");

# We can retrieve the port number for node 1 from nodectl in json form...

my $json2 = `$ENV{EDGE_N1}/pgedge/nc --json info pg17`;
# print("my json = $json2");
my $out2 = decode_json($json2);
$ENV{EDGE_PORT1} = $out2->[0]->{"port"};
print("The port number on node 1 is {$ENV{EDGE_PORT1}}\n");


# We can retrieve the home directory for node 2 from nodectl in json form... 

my $json3 = `$ENV{EDGE_N2}/pgedge/nc --json info`;
# print("my json = $json3");
my $out3 = decode_json($json3);
$ENV{EDGE_HOMEDIR2} = $out3->[0]->{"home"};
print("The home directory of node 2 is {$ENV{EDGE_HOMEDIR2}}\n");

# We can retrieve the port number for node 2 from nodectl in json form...

my $json4 = `$ENV{EDGE_N2}/pgedge/nc --json info pg17`;
# print("my json = $json4");
my $out4 = decode_json($json4);
$ENV{EDGE_PORT2} = $out4->[0]->{"port"};
print("The port number of node 2 is {$ENV{EDGE_PORT2}}\n");

# Then, drop the subscription on node 1:

my $cmd11 = qq($ENV{EDGE_HOMEDIR2}/nodectl spock sub-drop sub_n2n1 $ENV{EDGE_DB});
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
#print("stdout_buf11 = @$stdout_buf11\n");

# Then, we connect with psql and confirm that the subscription exists.

my $cmd7 = qq($ENV{EDGE_HOMEDIR2}/$ENV{EDGE_VERSION}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_PORT1} -d $ENV{EDGE_DB} -c "SELECT * FROM spock.subscription");
#print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

#print("stdout_buf7=$stdout_buf7\n");

 if(contains(@$stdout_buf11[0], "sub_drop"))

{
    exit(0);
}
else
{
    exit(1);
}
