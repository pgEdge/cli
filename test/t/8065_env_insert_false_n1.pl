# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.
# After creating the repset, we'll query the spock.replication_set_table to see if the repset exists. 


use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
use DBI;
use List::MoreUtils qw(pairwise);
no warnings 'uninitialized';

# Our parameters are:
my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory is $homedir1\n"); 

print("The port number is $ENV{EDGE_START_PORT}\n");


my $cmd5 = qq($homedir1/$ENV{EDGE_CLI} spock repset-create --replicate_insert=False demo-repset $ENV{EDGE_DB});
print("cmd5 = $cmd5\n");
my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);
print("stdout_buf5 = @$stdout_buf5\n");
print("We just executed the command that creates the replication set (demo-repset)\n");
print("\n");


if(!(contains(@$stdout_buf5[0], "repset_create")))
{
    exit(1);
} 


print("="x100,"\n");


##Table validation

my $dbh = DBI->connect("dbi:Pg:dbname=$ENV{EDGE_DB};host=$ENV{EDGE_HOST};port= $ENV{EDGE_START_PORT}",$ENV{EDGE_USERNAME},$ENV{EDGE_PASSWORD});

my $table_exists = $dbh->table_info(undef, 'public', 'foo', 'TABLE')->fetch;

if ($table_exists) {
    print "Table 'foo' already exists in the database.\n";
    
    print("\n");
} 

else
{
# Creating public.foo Table


 
    my $cmd6 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "CREATE TABLE foo (col1 INT PRIMARY KEY)");
    
    print("cmd6 = $cmd6\n");
    
    my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
    print("stdout_buf6 = @$stdout_buf6\n");
    
   if(!(contains(@$stdout_buf6[0], "CREATE TABLE")))
{
    exit(1);
}
   
   print ("-"x100,"\n"); 
   
  
     # Inserting into public.foo table

   my $cmd7 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "INSERT INTO foo select generate_series(1,10)");

   print("cmd7 = $cmd7\n");
   my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
      print("stdout_buf7 = @$stdout_buf7\n");
   if(!(contains(@$stdout_buf7[0], "INSERT")))
{
    exit(1);
}
   }
   
   print("="x100,"\n");
   
    
  #checking repset
  
  my $cmd9 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM spock.replication_set where set_name='demo-repset'");
   print("cmd9 = $cmd9\n");
   my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
   print("stdout_buf9= @$stdout_buf9\n");
  print("="x100,"\n");
  

  #
  # Listing repset tables 
  #
    my $json3 = `$homedir1/$ENV{EDGE_CLI} spock repset-list-tables public $ENV{EDGE_DB}`;
   print("my json3 = $json3");
   my $out3 = decode_json($json3);
   $ENV{EDGE_SETNAME} = $out3->[0]->{"set_name"};
   print("The set_name is = $ENV{EDGE_SETNAME}\n");
   print("="x100,"\n");
   
#Adding Table to the Repset 

if($ENV{EDGE_SETNAME} eq ""){
  
  
       my $cmd8 = qq($homedir1/$ENV{EDGE_CLI} spock repset-add-table demo-repset public.foo $ENV{EDGE_DB});
    
     print("cmd8 = $cmd8\n");
     my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
     print("stdout_buf8 = @$stdout_buf8\n");
     
     if(!(contains(@$stdout_buf8[0], "Adding table")))
{
    exit(1);
}
      
} 


else {
   print ("Table foo is already added to demo-repset\n");
    
   
}

print("="x100,"\n");

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd10 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM spock.replication_set");
print("cmd10 = $cmd10\n");
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);
#print("stdout_buf10 = @$stdout_buf10\n");

# Test to confirm that cluster is set up.



if(contains(@$stdout_buf10[0], "demo-repset"))

{
    exit(0);
}
else
{
    exit(1);
}


