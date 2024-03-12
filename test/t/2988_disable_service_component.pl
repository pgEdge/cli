# This test case runs the command:
# ./nc service disable pgV
# and performs the necessary validation before and after.

# Test 'service disable' disables a pgV service that cannot be started until enabled. 
# TODO : This test currently fails as service disable doesn't actually disable the service at the service (systemctl)
# level and that you can start the service again (without enabling it) even though it shows the service status to be
# disabled. 
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
my $isDisabled = 0;
#
# We use nodectl to service disable pgV
# 

# Checking service status (which at this point in the schedule should be a running service)
my $cmd0 = qq($homedir/$cli service status $pgversion);
print("cmd = $cmd0\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd0))[3];
print("stdout_buf : @$stdout_buf \n");
 
# Check if the pgV service is running so we can disable it 
if (contains($stdout_buf->[0], "running on port"))
 {
    # disable the service
    my $cmd = qq($homedir/$cli service disable $pgversion);
    print("cmd = $cmd\n");
    my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
    print("stdout_buf : @$stdout_buf \n");
    # if service disable was successful, it would have stopping pgV in its stdout buffer 
    if(contains($stdout_buf->[0], "stopping"))
    {
        print("$pgversion stopped \n");
        print("Check if service status shows disabled status \n");
        $stdout_buf = (run_command_and_exit_iferr (qq($homedir/$cli service status $pgversion)))[3];
        # confirm the service status to be disabled
        if(contains(@$stdout_buf, "disabled"))
        {
            print("service status returns service status as disabled\n");
            $isDisabled = 1;
        }
        else
        {
            print("service status does NOT return status as disabled\n");
            $isDisabled = 0;
        }

    }
    else
    {
        print("Could not disable $pgversion\n");
        $isDisabled = 0;
    }
}
else 
{
    print("$pgversion not running. Exiting with failure\n");
    exit(1);
}

# Now attempt to start a disabled service, that should fail however the disable functionality is yet to be fully implemented
# so this scenario below will be able to start the service (which at this point would be a test case failure)
if ($isDisabled)
{
    my $cmd1 = qq($homedir/$cli service start $pgversion);
    print("cmd = $cmd1\n");
    my ($stdout_buf1)= (run_command_and_exit_iferr ($cmd1))[3];
    print("stdout_buf : @$stdout_buf1");
    # TODO : At present, nodectl is able to start a disabled service and therefore this test fails
    if (contains(@$stdout_buf1,"starting on port"))
    {
        print("nodectl is able to start a disabled service. Exiting with failure");
        exit(1);
    }
    else
    {
        print("nodectl is unable to start a disabled service. Success");
        exit(0);
    }

}
else
{
    print("nodectl was not able to disable the service successfully. Exiting with failure");
    exit(1);
} 



=pod
use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './lib';
use contains;

my $comp2;
my $comp;
my $assign;

chdir("./pgedge");


my $cmd1 = qq(./nc list);
my ($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1) = IPC::Cmd::run(command => $cmd1, verbose => 0);

#print ("success = $success\n");
#print("stderr_buf = @$stderr_buf\n");


if ($success1) {
   
    foreach my $out1(@$full_buf1) {
        print ("$out1\n");
       
    }
} else {
    die "Error running command: $error_message1";
}

my $cmd2 = qq(./nc list --json);
 
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2) = IPC::Cmd::run(command => $cmd2, verbose => 0);

my $json = `./nc list --json`;

my $out2 = decode_json($json);


foreach $comp (@$out2){
  
      my $compName = $comp->{component};
   
      print "Component Name:$compName\n";
    
      my $json2 = `./nc --json info $compName`;
    
      my $out3 = decode_json($json2);
    
    #print "json2 =$json2\n";
    
  foreach $comp2 (@$out3){
      
      my $is_installed = $comp2->{is_installed};
       
      #print "is_installed = $is_installed\n";
       
       if ($is_installed == 1)
       {
       
        print "Component $compName Installed\n";
           
        my $cmd3 = qq(./nc service status -c $compName);
        
        print("cmd3 = $cmd3\n");
           
        my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

        print("full_buf3 = @$full_buf3\n");
        print ("-"x65,"\n");  
    =cut      
=head
if(contains(@$stdout_buf3[0], "starting"))

{
    
    exit(0);
}
else
{
    exit(1);
}
=cut
=pod
       }

       
       else
       {           
      my $cmd4 = qq(./nc service disable -c $compName);
        
      print("cmd4 = $cmd4\n");
      
      my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

     print("full_buf4 = @$full_buf4\n");
     
        
      my $cmd5 = qq(./nc service status -c $compName);
        
      print("cmd5 = $cmd5\n");
           
      my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

      print("full_buf5 = @$full_buf5\n");
     
      
      print ("-"x65,"\n");  
	 
	  
       }
    }
}

=cut
