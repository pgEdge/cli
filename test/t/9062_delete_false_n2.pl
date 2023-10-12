# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we will create the --repset_delete=False on node2.
#created table
#Added table to repset
# After creating the repset, we'll query the spock.replication_set_table to see if the repset exists. 


use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './lib';
use contains;
use List::MoreUtils qw(pairwise);

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
my $repset = "demo-nodelete-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory from nodectl in json form... 

my $json = `$n2/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n"); 

# We can retrieve the port number from nodectl in json form...
my $json1 = `$n2/pgedge/nc --json info pg16`;
# print("my json = $json1");
my $out1 = decode_json($json1);
my $port = $out1->[0]->{"port"};
print("The port number is {$port}\n");



# Register node 2 and the repset entry on n2: 
print("repuser before chomp = $repuser\n");
chomp($repuser);

#Creating repset (demo-noinsert-repset) 
#
## 
my $cmd3 = qq($homedir/nodectl spock repset-create --replicate_delete=False $repset $database);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("success3 = $success3\n");
print("stdout_buf3 = @$stdout_buf3\n");

print("We just executed the command that creates the replication set (demo-nodelete-repset)\n");

print ("-"x150,"\n");

     # Creating public.foo_no_insert Table

    my $cmd6 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "CREATE TABLE public.foo_no_delete (col1 INT PRIMARY KEY)");
    print("cmd6 = $cmd6\n");
    my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
    print ("-"x150,"\n");
    print("\n");

    my $cmd9 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.tables");
     print("cmd9 = $cmd9\n");
   my ($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
     
     print("stdout_buf9= @$stdout_buf9\n");

   print ("-"x150,"\n");
   print("\n");

    # Inserting into public.foo table

   my $cmd7 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "INSERT INTO public.foo_no_delete select generate_series(1,10)");
   print("cmd7 = $cmd7\n");
   my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
   
    print("\n");
   print ("-"x150,"\n");
 print("\n");
  

   
   #Adding Table to the Repset

    my $cmd8 = qq($homedir/nodectl spock repset-add-table $repset public.foo_no_delete $database);
    print("cmd8 = $cmd8\n");
    my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
    print("stdout_buf8 = @$stdout_buf8\n");
    
    print ("-"x150,"\n");
    print("\n");
  
 # Then, use the info to connect to psql and test for the existence of the replication set.
 my $cmd5 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set WHERE set_name='$repset'");
 print("cmd5 = $cmd5\n");
 my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);




if(contains(@$stdout_buf5[0], "demo-nodelete-repset"))

{
    exit(0);
}
else
{
    exit(1);
}



