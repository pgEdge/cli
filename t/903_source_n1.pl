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


my $cmd6 = qq(source $n1/$version/$version.env);
print("cmd6 = $cmd6\n");
my ($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);

#print("full_buf6 = @$full_buf6\n");
#print("stderr_buf6 = @$stderr_buf6\n");
print("We just sourced the environment variables in n1\n");

#
# Test
#

if (defined($success6))
{
    exit(0);
}
else
{
    exit(1);
}


