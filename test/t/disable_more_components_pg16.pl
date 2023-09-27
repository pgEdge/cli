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
my $version= "pg16";

chdir("./pgedge");




my $cmd2 = qq(./nc list --json);
 
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2) = IPC::Cmd::run(command => $cmd2, verbose => 0);

my $json = `./nc list --json`;

my $out2 = decode_json($json);


foreach $comp (@$out2){
  
      my $compName = $comp->{component};
   
        print "Component Name:$compName\n";
    
      my $json2 = `./nc --json info $compName`;
    
      my $out3 = decode_json($json2);
    
        print "json2 =$json2\n";
    
  foreach $comp2 (@$out3){
      
      my $is_installed = $comp2->{is_installed};
       
        print "is_installed = $is_installed\n";
      
       
        print "Component $compName Installed\n";
           
      my $cmd3 = qq(./nc service disable -c $version $compName);
        
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
    }



