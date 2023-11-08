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

print("whoami = $ENV{EDGE_REPUSER}\n");

# We can retrieve the home directory from nodectl in json form... 

my $json = `$ENV{EDGE_N1}/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
$ENV{EDGE_HOMEDIR1} = $out->[0]->{"home"};

print("The home directory is $ENV{EDGE_HOMEDIR1}\n"); 

# We can retrieve the port number from nodectl in json form...

my $json2 = `$ENV{EDGE_N1}/pgedge/nc --json info $ENV{EDGE_VERSION}`;
#print("my json = $json2");
my $out2 = decode_json($json2);
$ENV{EDGE_PORT1} = $out2->[0]->{"port"};

print("The port number is $ENV{EDGE_PORT1}\n");



my $cmd3 = qq($ENV{EDGE_HOMEDIR1}/nodectl spock repset-drop $ENV{EDGE_REPSET} $ENV{EDGE_DB});
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











