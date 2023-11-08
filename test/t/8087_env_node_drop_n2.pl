# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll drop the node 1.



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

# We can retrieve the home directory from nodectl in json form... 

my $json = `$ENV{EDGE_N2}/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
 $ENV{EDGE_HOMEDIR2} = $out->[0]->{"home"};
print("The home directory is $ENV{EDGE_HOMEDIR2}\n"); 

# We can retrieve the port number from nodectl in json form...

my $json2 = `$ENV{EDGE_N2}/pgedge/nc --json info $ENV{EDGE_VERSION}`;
#print("my json = $json2");
my $out2 = decode_json($json2);
 $ENV{EDGE_PORT2} = $out2->[0]->{"port"};
print("The port number is $ENV{EDGE_PORT2}\n");

# Drop n2 node

my $cmd2 = qq($ENV{EDGE_HOMEDIR2}/nodectl spock node-drop n2 $ENV{EDGE_DB});
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout_buf2 = @$stdout_buf2\n");



if(contains(@$stdout_buf2[0], "node_drop"))

{
    exit(0);
}
else
{
    exit(1);
}

