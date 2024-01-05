# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll drop the repset on node1.
 

 
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
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory is $homedir1\n"); 

print("The port number is $ENV{EDGE_START_PORT}\n");

my $cmd3 = qq($homedir1/$ENV{EDGE_CLI} spock repset-drop demo-repset $ENV{EDGE_DB});
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("success3 = $success3\n");
#print("stdout_buf3 = @$stdout_buf3\n");

  
 if(contains(@$stdout_buf3[0], "repset_drop"))

{
    exit(0);
}
else
{
    exit(1);
}











