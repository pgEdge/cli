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
#pgedge home directory for n1
my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $exitcode = 0;
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory is $homedir1\n"); 

print("The port number is $ENV{EDGE_START_PORT}\n");

#
## Check for n1 node existence

my $json3 = `$homedir1/$ENV{EDGE_CLI} spock node-list  $ENV{EDGE_DB}`;
   #print("my json3 = $json3");
my $out3 = decode_json($json3);
  $ENV{EDGE_NODE1_NAME} = $out3->[0]->{"node_name"};
   print("The node_name is = $ENV{EDGE_NODE1_NAME}\n");
      
if($ENV{EDGE_NODE1_NAME} eq "")
{   
   my $cmd2 = qq($homedir1/$ENV{EDGE_CLI} spock node-create n1 'host=$ENV{EDGE_HOST} port=$ENV{EDGE_START_PORT} user=$ENV{EDGE_REPUSER} dbname=$ENV{EDGE_DB}' $ENV{EDGE_DB});
   print("cmd2 = $cmd2\n");
   my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
   print("stdout_buf2 = @$stdout_buf2\n");
}
else 
{ 
 print("Node $ENV{EDGE_NODE1_NAME} already exists\n");
 $exitcode = 1;
}

my $json4 = `$homedir1/$ENV{EDGE_CLI} spock node-list  $ENV{EDGE_DB}`;
   #print("my json3 = $json3");
my $out4 = decode_json($json4);
  $ENV{EDGE_NODE1_NAME} = $out4->[0]->{"node_name"};
   print("The node_name is = $ENV{EDGE_NODE1_NAME}\n");
      

if($ENV{EDGE_NODE1_NAME} eq "n1" && $exitcode==0)
{
    exit(0);
}
else
{
    exit(1);
}







