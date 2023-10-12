# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.
# Checks Table existence
# Checks Repset through spock.replication_set
# Checks tables through nc spock repset-list-tables
# Validation of adding Table to repset
# Check for the existence of replication set

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './lib';
use contains;
use DBI;
use List::MoreUtils qw(pairwise);
no warnings 'uninitialized';


# Our parameters are:

my $cmd99 = qq(whoami);
print("cmd99 = $cmd99\n");
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-noinsert-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";
my $schema = "public";
my $table_name="foo_no_insert";

# We can retrieve the home directory from nodectl in json form... 

my $json = `$n1/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
#print("The home directory is {$homedir}\n"); 

my $json4 =`$n2/pgedge/nc --json info`;
# print("my json = $json");
my $out4 = decode_json($json4);
my $homedir2 = $out4->[0]->{"home"};
#print("The home directory is {$homedir2}\n"); 


# We can retrieve the port number from nodectl in json form...
my $json1 = `$n1/pgedge/nc --json info pg16`;
# print("my json = $json1");
my $out1 = decode_json($json1);
my $port1 = $out1->[0]->{"port"};
#print("The port number is {$port1}\n");

my $json2 = `$n2/pgedge/nc --json info pg16`;
# print("my json = $json1");
my $out2 = decode_json($json2);
my $port2 = $out2->[0]->{"port"};
#print("The port number is {$port2}\n");


print("repuser before chomp = $repuser\n");
chomp($repuser);


#====================================================================================================================================================
# Checking Replication --insert=False
   
    print("INSERT=FALSE REPLICATION CHECK\n");
    print ("-"x45,"\n");
    my $cmd6= qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "INSERT INTO $schema.$table_name values(555)");
    print("cmd6 = $cmd6\n");
    my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
    
    print("stdout_buf6= @$stdout_buf6\n");
    
    
   print ("-"x100,"\n"); 
    print("INSERT=FALSE REPLICATION CHECK IN NODE n1 \n");
     print ("-"x45,"\n");
      # Listing table contents of Port1 6432
    my $cmd9 = qq($homedir/$version/bin/psql  -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM $table_name");
   print("cmd9 = $cmd9\n");
   my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
   print("stdout_buf9= @$stdout_buf9\n");
  print("="x100,"\n");
  
  # Listing table contents of Port2 6433
   print("INSERT=FALSE REPLICATION CHECK IN NODE n2\n");
    print ("-"x45,"\n");
  my $cmd10 = qq($homedir2/$version/bin/psql  -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM $table_name");
   print("cmd10 = $cmd10\n");
   my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);
   print("stdout_buf10= @$stdout_buf10\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf6[0], "INSERT")))
{
    exit(1);
}
 


  #====================================================================================================================================================
  
  #Checking Replication delete=True
    print("DELETE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd7 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "DELETE FROM $schema.$table_name where col1=2");
    print("cmd7 = $cmd7\n");
    my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
   
   print ("-"x100,"\n"); 
    
      # Listing table contents of Port1 6432
      
     print("DELETE FUNCTION REPLICATION CHECK IN NODE n1 \n");
      print ("-"x45,"\n"); 
    my $cmd8 = qq($homedir/$version/bin/psql  -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM $table_name");
   print("cmd8 = $cmd8\n");
   my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
   print("stdout_buf8= @$stdout_buf8\n");
  print("="x100,"\n");
  
  # Listing table contents of Port2 6433
    print("DELETE FUNCTION REPLICATION CHECK IN NODE n2 \n");
    print ("-"x45,"\n");
  my $cmd11 = qq($homedir2/$version/bin/psql  -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM $table_name");
   print("cmd11 = $cmd11\n");
   my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
   print("stdout_buf11= @$stdout_buf11\n");
  print("="x100,"\n");
  
  #======================================================================================================================================================================
  
   #Checking Replication update=True
    print("UPDATE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd12 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "UPDATE $table_name SET col1=333 where col1=3");
    print("cmd12 = $cmd12\n");
    my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
   
   print ("-"x100,"\n"); 
    
      # Listing table contents of Port1 6432
      
     print("UPDATE FUNCTION REPLICATION CHECK IN NODE n1 \n");
      print ("-"x45,"\n"); 
    my $cmd13 = qq($homedir/$version/bin/psql  -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM $table_name");
   print("cmd8 = $cmd8\n");
   my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
   print("stdout_buf13= @$stdout_buf13\n");
  print("="x100,"\n");
  
  # Listing table contents of Port2 6433
   print("UPDATE FUNCTION REPLICATION CHECK IN NODE n2\n");
    print ("-"x45,"\n");
  my $cmd14 = qq($homedir2/$version/bin/psql  -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM $table_name");
   print("cmd14 = $cmd14\n");
   my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
   print("stdout_buf14= @$stdout_buf14\n");
  print("="x100,"\n");
  
  #========================================================================================================================================================================
  
    #Checking Replication Truncate=True
    print("TRUNCATE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd15 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "TRUNCATE $table_name");
    print("cmd15 = $cmd15\n");
    my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
   
   print ("-"x100,"\n"); 
    
      # Listing table contents of Port1 6432
      
     print("	      TRUNCATE FUNCTION REPLICATION CHECK IN NODE n1\n"); 
      print ("-"x45,"\n"); 
    my $cmd16 = qq($homedir/$version/bin/psql  -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM $table_name");
   print("cmd16 = $cmd16\n");
   my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);
   print("stdout_buf16= @$stdout_buf16\n");
  print("="x100,"\n");
  
  # Listing table contents of Port2 6433
   print("TRUNCATE FUNCTION REPLICATION CHECK IN NODE n2\n");
    print ("-"x45,"\n");
  my $cmd17 = qq($homedir2/$version/bin/psql  -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM $table_name");
   print("cmd17 = $cmd17\n");
   my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);
   print("stdout_buf17= @$stdout_buf17\n");
  print("="x100,"\n");
  
  #================================================================================================================================================================================
  
  #Generating series in table of port 1 6432

 print("GENERATING SERIES IN TABLE IN n1");
   my $cmd18 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port1 -d $database -c "INSERT INTO public.$table_name select generate_series(1,10)");
   print("cmd18 = $cmd18\n");
   my($success18, $error_message18, $full_buf18, $stdout_buf18, $stderr_buf18)= IPC::Cmd::run(command => $cmd18, verbose => 0);
 
   print("="x100,"\n");
   
   my $cmd20 = qq($homedir/$version/bin/psql  -h 127.0.0.1 -p $port1 -d $database -c "SELECT * FROM $table_name");
   print("cmd20 = $cmd20\n");
   my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
   print("stdout_buf20= @$stdout_buf20\n");
  print("="x100,"\n");
 
   
   #================================================================================================================================================================================

   
  #Generating series in table of port 2 6433

   print("GENERATING SERIES IN TABLE IN n2");
   my $cmd19 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "INSERT INTO public.$table_name select generate_series(1,10)");
   print("cmd19 = $cmd19\n");
   my($success19, $error_message19, $full_buf19, $stdout_buf19, $stderr_buf19)= IPC::Cmd::run(command => $cmd19, verbose => 0);
 
   print("="x100,"\n");
   
  
    
  my $cmd21 = qq($homedir2/$version/bin/psql  -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM $table_name");
   print("cmd21 = $cmd21\n");
   my($success21, $error_message21, $full_buf21, $stdout_buf21, $stderr_buf21)= IPC::Cmd::run(command => $cmd21, verbose => 0);
   print("stdout_buf21= @$stdout_buf21\n");
  print("="x100,"\n");
  

   #==================================================================================================================================================================================


