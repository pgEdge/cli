# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 2 and create the repset on that node.
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
#pgedge home directory for n2
my $homedir2="$ENV{EDGE_CLUSTER_DIR}/n2/pgedge";
#add 1 to the default port for use with node n2
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;
print("whoami = $ENV{EDGE_REPUSER}\n");


# We can retrieve the home directory from nodectl in json form... 

print("The home directory is $homedir2\n"); 

print("The port number is $myport2\n");

#
## Check for n2 node existence

my $json3 = `$ENV{EDGE_CLUSTER_DIR}/n2/pgedge/nc spock node-list  $ENV{EDGE_DB}`;
   #print("my json3 = $json3");
my $out3 = decode_json($json3);
  $ENV{EDGE_NODE2_NAME} = $out3->[0]->{"node_name"};
   print("The node_name is = $ENV{EDGE_NODE2_NAME}\n");
   
   
if($ENV{EDGE_NODE2_NAME} eq "")

   {
   
my $cmd2 = qq($homedir2/nodectl spock node-create n2 'host=$ENV{EDGE_HOST} port=$myport2 user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
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




