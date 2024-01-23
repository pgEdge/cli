# This test case runs the command:
# ./nc um list
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


my $homedir = "$ENV{EDGE_HOME_DIR}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $cli = "$ENV{EDGE_CLI}";


my $cmd = qq($homedir/$cli um list);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success)) 
{
    if(!(is_umlist_component_installed($stdout_buf, "$pgversion")))
    {
        print("$pgversion not installed. Exiting with code 1\n");
        exit(1);
    }
} 
else
{
    print("$cmd not executed successfully. stderr buffer :  @$full_buf\n");
    exit(1);
} 

exit(0);

=pod
#
# Move into the pgedge directory
#

#chdir ("./pgedge");

# 
# We are now exercising the ./nc um list variation; a successful run returns 1.
#

my $cmd2 = qq(./nc um list);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("success2 = $success2\n");
print("error_message2 = $error_message2\n");
print("full_buf2 = @$full_buf2\n");
print("stdout_buf2 = @$stdout_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");

my $value = $success2;

if (defined($value))
{
    exit(0);
}
else
{
    exit(1);
}
=cut
