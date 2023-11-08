# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.
# After creating the repset, we'll query the spock.replication_set_table to see if the repset exists. 


use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
no warnings 'uninitialized';

# Our parameters are:

print("whoami = $ENV{EDGE_REPUSER}\n");


# We can retrieve the home directory from nodectl in json form... 


my $json = `$ENV{EDGE_N2}/pgedge/nc --json info`;
my $out = decode_json($json);
$ENV{EDGE_HOMEDIR2} = $out->[0]->{"home"};
print("The home directory is $ENV{EDGE_HOMEDIR2}\n"); 

# We can retrieve the port number from nodectl in json form...
my $json2 = `$ENV{EDGE_N2}/pgedge/nc --json info $ENV{EDGE_VERSION}`;
#print("my json = $json2");
my $out2 = decode_json($json2);
$ENV{EDGE_PORT2} = $out2->[0]->{"port"};
 print("The port number is $ENV{EDGE_PORT2}\n");


#
## Check for n2 node existence

my $json3 = `$ENV{EDGE_N2}/pgedge/nc spock node-list  $ENV{EDGE_DB}`;
   #print("my json3 = $json3");
my $out3 = decode_json($json3);
  $ENV{EDGE_NODE2_NAME} = $out3->[0]->{"node_name"};
   print("The node_name is = $ENV{EDGE_NODE2_NAME}\n");
   
   
if($ENV{EDGE_NODE2_NAME} eq "")

   {
   
my $cmd2 = qq($ENV{EDGE_HOMEDIR2}/nodectl spock node-create n2 'host=$ENV{EDGE_HOST} port=$ENV{EDGE_PORT2} user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("stdout_buf2 = @$stdout_buf2\n");

if(contains(@$stdout_buf2[0], "node_create"))

{
    exit(0);
}
else
{
    exit(1);
}
}

else {
 
 print("Node $ENV{EDGE_NODE1_NAME} already exists\n");

}




