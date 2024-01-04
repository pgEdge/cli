# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll drop table created on node 1.



use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
use List::MoreUtils qw(pairwise);
no warnings 'uninitialized';
 
# Our parameters are:
#pgedge home directory for n1
my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";

print("whoami = $ENV{EDGE_REPUSER}\n");

print("The home directory is $homedir1\n"); 

print("The port number is $ENV{EDGE_START_PORT}\n");


     print ("-"x150,"\n");

     # Dropping public.foo Table

     my $cmd6 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "DROP TABLE public.foo CASCADE");
     print("cmd6 = $cmd6\n");
     my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
     #print("full6 = @$full_buf6\n");
     print ("-"x150,"\n");

     #print("success6 = $success6\n");
      print("stdout_buf6 = @$stdout_buf6\n");
    

     my $cmd7 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM spock.tables");
     #print("cmd7 = $cmd7\n");
     my ($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

        #print("success7 = $success7\n");
       

if(contains(@$stdout_buf6[0], "DROP TABLE"))

{
    exit(0);
}
else
{
    exit(1);
}


 



