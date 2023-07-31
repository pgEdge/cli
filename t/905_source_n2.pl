# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1/pgedge";
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2/pgedge";

# Source the environment variables on n2 as well:
#

my $cmd8 = qq(source $n2/$version/$version.env);
print("cmd8 = $cmd8\n");
my ($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);

#print("full_buf8 = @$full_buf8\n");
#print("stderr_buf8 = @$stderr_buf8\n");
print("We just sourced the environment variables in n2\n");

#
# Test
#

if (defined($success8))
{
    exit(0);
}
else
{
    exit(1);
}

