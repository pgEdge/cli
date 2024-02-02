# This test case runs the command:
# ./nc service enable pgV
# and performs the necessary validation before and after.

# Test 'service enable' enables a pgV service that is disabled. 
# TODO : This test currently fails as service disable does not work as expected and therefore enabling a service
# (whether disabled or already enabled) does nothing. When the service disable is addressed, the service enable 
# will also be addressed with it. 
use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $homedir = "$ENV{EDGE_HOME_DIR}";
my $cli = $ENV{EDGE_CLI};
my $pgversion = $ENV{EDGE_COMPONENT};
my $isEnabled = 0;
#
# We use nodectl to service disable pgV
# 

# Checking service status (which at this point in the schedule after 2988 should be disabled)
# Note : Due to 2988 failing (service disable not disabling the actual service), this test 
# case would first disable the service and then enable it. 
# Once 2988 is addressed, this test case will have to have enhanced. 

my $cmd0 = qq($homedir/$cli service disable $pgversion);
print("cmd = $cmd0\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd0))[3];
print("stdout_buf : @$stdout_buf \n");

# Check status that should show service as disabled
$cmd0 = qq($homedir/$cli service status $pgversion);
print("cmd = $cmd0\n");
$stdout_buf= (run_command_and_exit_iferr ($cmd0))[3];
print("stdout_buf : @$stdout_buf \n");
 
# Check if the service disable command above stopped the running service 
if (contains(@$stdout_buf[0], "disabled"))
 {
    # enable the service
    my $cmd = qq($homedir/$cli service enable $pgversion);
    print("cmd = $cmd\n");
    my $stdout_buf= (run_command_and_exit_iferr ($cmd))[3];
    print("stdout_buf : @$stdout_buf \n");
    # service enable at this point does not provide any confirmation so the buffer will be empty, 
    # once we know what the confirmation message will be, the if condition will be udpated.
    # enable this when theres a new confirmation message  if(contains(@$stdout_buf[0], "<enable confirmation message>"))
    
    print("Check if service status is not disabled anymore \n");
    $stdout_buf = (run_command_and_exit_iferr (qq($homedir/$cli service status $pgversion)))[3];
    # confirm the service status to be disabled
    if(!contains(@$stdout_buf, "disabled"))
    {
        print("service enabled. Expected\n");
        $isEnabled = 1;
    }
    else
    {
        print("service still disabled. Unexpected\n");
        $isEnabled = 0;
    }
}

# Now attempt to start an enabled service to confirm the service is successfully started. 

if ($isEnabled)
{
    my $cmd1 = qq($homedir/$cli service start $pgversion);
    print("cmd = $cmd1\n");
    my ($stdout_buf1)= (run_command_and_exit_iferr ($cmd1))[3];
    print("stdout_buf : @$stdout_buf1");
    # TODO : At present, nodectl is able to start a disabled service and therefore this test fails
    if (contains(@$stdout_buf1,"starting on port"))
    {
        print("nodectl is able to start an enabled service. Success");
        print("Intentionally doing an exit 1 and failing this test as service enable functionality\n will be reworked and revalidated along with disable");
        exit(1);
    }
    else
    {
        print("nodectl is unable to start an enabled service. Failure");
        exit(1);
    }

}
else
{
    print("nodectl was not enabled successfully. Exiting with failure");
    exit(1);
} 


