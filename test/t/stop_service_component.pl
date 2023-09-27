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
       }

       
       else
       { 
       
      
    
      my $out3 = decode_json($json2);
     
      my $is_installed1 = $comp2->{is_installed}; 
         
        if ($is_installed1 != 1)
       { 
                 
              my $cmd4 = qq(./nc service stop -c $compName);
              
              	#print "json2 =$json2\n";
        
              print("cmd4 = $cmd4\n");
      
              my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

              #print("full_buf4 = @$full_buf4\n");      
        
              my $cmd5 = qq(./nc service status -c $compName);
        
              print("cmd5 = $cmd5\n");
      
              my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

              print("full_buf5 = @$full_buf5\n"); 
     
             print ("-"x65,"\n");  
       
	} 
	  
       }
    }
}


