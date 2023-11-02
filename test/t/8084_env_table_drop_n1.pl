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


print("whoami = $ENV{EDGE_REPUSER}\n");


# We can retrieve the home directory from nodectl in json form... 

my $json = `$ENV{EDGE_N1}/pgedge/nc --json info`;
# print("my json = $json");
my $out = decode_json($json);
$ENV{EDGE_HOMEDIR1} = $out->[0]->{"home"};
print("The home directory is $ENV{EDGE_HOMEDIR1}\n"); 

# We can retrieve the port number from nodectl in json form...

my $json1 = `$ENV{EDGE_N1}/pgedge/nc --json info $ENV{EDGE_VERSION}`;
# print("my json = $json1");
my $out1 = decode_json($json1);
 $ENV{EDGE_PORT1} = $out1->[0]->{"port"};
print("The port number is $ENV{EDGE_PORT1}\n");


     print ("-"x150,"\n");

     # Dropping public.foo Table

     my $cmd6 = qq($ENV{EDGE_HOMEDIR1}/$ENV{EDGE_VERSION}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_PORT1} -d $ENV{EDGE_DB} -c "DROP TABLE $ENV{EDGE_TABLE} CASCADE");
     print("cmd6 = $cmd6\n");
     my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
     #print("full6 = @$full_buf6\n");
     print ("-"x150,"\n");

     #print("success6 = $success6\n");
      print("stdout_buf6 = @$stdout_buf6\n");
    

     my $cmd7 = qq($ENV{EDGE_HOMEDIR1}/$ENV{EDGE_VERSION}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_PORT1} -d $ENV{EDGE_DB} -c "SELECT * FROM spock.tables");
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


 



