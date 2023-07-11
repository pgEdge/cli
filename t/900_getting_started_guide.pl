# This is a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

#
# Move into the pgedge directory.
#
 chdir("./pgedge");

#
# Create a variable with the path to each node.
# 

my $n1 = "~/work/nodectl/pgedge/cluster/demo/n1"; 
my $n2 = "~/work/nodectl/pgedge/cluster/demo/n2";

#
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default).
# 

my $cmd = qq(./nodectl cluster create-local demo 2 --pg 16);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");
print("This s/b a 2 node cluster named demo, owned by lcdb, with a db named lcdb.  The nodes are named n1/n2.\n");
print("This test assumes they're running on 6432 and 6433\n");

#
# Register node 1 and the repset entry on n1: 
#

my $cmd2 = qq($n1/nodectl spock node-create n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd2 = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);

print("full_buf2 = @$full_buf2\n");
print("stderr_buf2 = @$stderr_buf2\n");
print("We just invoked the ./nc spock node-create n1 command\n");


my $cmd3 = qq($n1/nodectl spock repset-create demo_replication_set lcdb);
print("cmd3 = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("full_buf3 = @$full_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");
print("We just created the replication set (demo_replication_set\n");

#
# Register node 2 and add the replication set entry on n2: 
#

my $cmd4 = qq($n2/nodectl spock node-create n2 'host=127.0.0.1 port=6433 user=lcdb dbname=lcdb' lcdb);
print("cmd4 = $cmd4\n");
my ($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);

print("full_buf4 = @$full_buf4\n");
print("stderr_buf4 = @$stderr_buf4\n");
print("We just invoked the ./nc spock node-create n2 command\n");

my $cmd5 = qq($n2/nodectl spock repset-create demo_replication_set lcdb);
print("cmd5 = $cmd5\n");
my ($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);

print("full_buf5 = @$full_buf5\n");
print("stderr_buf5 = @$stderr_buf5\n");
print("We just created the replication set (demo_replication_set\n");

#
# Before you create the subscriptions, make lcdb a login user with an entry in the pgpass file.
#

my $cmd6 = qq(source $n1/pg16/pg16.env);
print("cmd6 = $cmd6\n");
my ($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);

#print("full_buf6 = @$full_buf6\n");
#print("stderr_buf6 = @$stderr_buf6\n");
print("We just sourced the environment variables in n1\n");

#
# Then, we connect with psql and update the user on n1.
#

my $cmd7 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "ALTER ROLE lcdb LOGIN PASSWORD 'password'");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);

print("success7 = $success7\n");
print("stdout_buf7 = @$stdout_buf7\n");

#
# Update the role attributes on n2 as well:
#

my $cmd8 = qq(source $n2/pg16/pg16.env);
print("cmd8 = $cmd8\n");
my ($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);

#print("full_buf8 = @$full_buf8\n");
#print("stderr_buf8 = @$stderr_buf8\n");
print("We just sourced the environment variables in n2\n");

#
# Then, we connect with psql and update the user on n2.
#

my $cmd9 = qq(psql -t -h 127.0.0.1 -p 6433 -d lcdb -c "ALTER ROLE lcdb LOGIN PASSWORD 'password'");
print("cmd9 = $cmd9\n");
my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);

print("success9 = $success9\n");
print("stdout_buf9 = @$stdout_buf9\n");

#
# Then, we add an entry to the ~/.pgpass file for the lcdb user so we can connect with psql.
#

my $cmd10 = qq(echo "*:*:*:lcdb:password" >> ~/.pgpass);
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);

print("We'll need to authenticate with this user later, so $cmd10 adds the password to the pgpass file.\n");

#
# Then, create the subscriptions:
#
#on node 1:

my $cmd11 = qq($n1/nodectl spock sub-create sub_n1n2 'host=127.0.0.1 port=6433 user=lcdb dbname=lcdb' lcdb);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);

print("success11 = $success11\n");
print("stdout_buf11 = @$stdout_buf11\n");

#on node 2:

my $cmd12 = qq($n2/nodectl spock sub-create sub_n2n1 'host=127.0.0.1 port=6432 user=lcdb dbname=lcdb' lcdb);
print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);

print("success12 = $success12\n");
print("stdout_buf12 = @$stdout_buf12\n");

my $cmd13 = qq(pgbench -i --port 6433 lcdb);
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);

print("We've just created pgbench artifacts on = {$n2}\n");

my $cmd14 = qq(pgbench -i --port 6432 lcdb);
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);

print("We've just created pgbench artifacts on = {$n1}\n");

#
# Set up pgbench on node 1
#

my $cmd15 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);

print("success15 = $success15\n");
print("stdout_buf15 = @$stdout_buf15\n");

my $cmd16 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);

print("success16 = $success16\n");
print("stdout_buf16 = @$stdout_buf16\n");

my $cmd17 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd17 = $cmd17\n");
my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);

print("success17 = $success17\n");
print("stdout_buf17 = @$stdout_buf17\n");

#
# Set up pgbench on node 2
#

my $cmd18 = qq(psql -t -h 127.0.0.1 -p 6433 -d lcdb -c "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)");
print("cmd18 = $cmd18\n");
my($success18, $error_message18, $full_buf18, $stdout_buf18, $stderr_buf18)= IPC::Cmd::run(command => $cmd18, verbose => 0);

print("success18 = $success18\n");
print("stdout_buf18 = @$stdout_buf18\n");

my $cmd19 = qq(psql -t -h 127.0.0.1 -p 6433 -d lcdb -c "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)");
print("cmd19 = $cmd19\n");
my($success19, $error_message19, $full_buf19, $stdout_buf19, $stderr_buf19)= IPC::Cmd::run(command => $cmd19, verbose => 0);

print("success19 = $success19\n");
print("stdout_buf19 = @$stdout_buf19\n");

my $cmd20 = qq(psql -t -h 127.0.0.1 -p 6433 -d lcdb -c "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true)");
print("cmd20 = $cmd20\n");
my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);

print("success20 = $success20\n");
print("stdout_buf20 = @$stdout_buf20\n");

#
# Then, on each node, invoke this command to add pgbench tables to the repset:
#

my $cmd21 = qq($n1/nodectl spock repset-add-table demo_replication_set 'pgbench_*' lcdb);
print("cmd21 = $cmd21\n");
my($success21, $error_message21, $full_buf21, $stdout_buf21, $stderr_buf21)= IPC::Cmd::run(command => $cmd21, verbose => 0);

print("success21 = $success21\n");
print("stdout_buf21 = @$stdout_buf21\n");

my $cmd22 = qq($n2/nodectl spock repset-add-table demo_replication_set 'pgbench_*' lcdb);
print("cmd22 = $cmd22\n");
my($success22, $error_message22, $full_buf22, $stdout_buf22, $stderr_buf22)= IPC::Cmd::run(command => $cmd22, verbose => 0);

print("success22 = $success22\n");
print("stdout_buf22 = @$stdout_buf22\n");

#
# Then, add the repsets to the subscriptions:
#

my $cmd23 = qq($n1/nodectl spock sub-add-repset sub_n1n2 demo_replication_set lcdb);
print("cmd23 = $cmd23\n");
my($success23, $error_message23, $full_buf23, $stdout_buf23, $stderr_buf23)= IPC::Cmd::run(command => $cmd23, verbose => 0);

print("success23 = $success23\n");
print("stdout_buf23 = @$stdout_buf23\n");

my $cmd24 = qq($n2/nodectl spock sub-add-repset sub_n2n1 demo_replication_set lcdb);
print("cmd24 = $cmd24\n");
my($success24, $error_message24, $full_buf24, $stdout_buf24, $stderr_buf24)= IPC::Cmd::run(command => $cmd24, verbose => 0);

print("success24 = $success24\n");
print("stdout_buf24 = @$stdout_buf24\n");

#
# Use psql to check the setup, and confirm replication is working.
#

my $cmd25 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "SELECT * FROM spock.node");
print("cmd25 = $cmd25\n");
my($success25, $error_message25, $full_buf25, $stdout_buf25, $stderr_buf25)= IPC::Cmd::run(command => $cmd25, verbose => 0);

print("success25 = $success25\n");
print("stdout_buf25 = @$stdout_buf25\n");

my $cmd26 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "SELECT sub_id, sub_name, sub_slot_name, sub_replication_sets  FROM spock.subscription");
print("cmd26 = $cmd26\n");
my($success26, $error_message26, $full_buf26, $stdout_buf26, $stderr_buf26)= IPC::Cmd::run(command => $cmd26, verbose => 0);

print("success26 = $success26\n");
print("stdout_buf26 = @$stdout_buf26\n");

my $cmd27 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "SELECT * FROM pgbench_tellers WHERE tid = 1");
print("cmd27 = $cmd27\n");
my($success27, $error_message27, $full_buf27, $stdout_buf27, $stderr_buf27)= IPC::Cmd::run(command => $cmd27, verbose => 0);

print("success27 = $success27\n");
print("stdout_buf27 = @$stdout_buf27\n");

my $cmd28 = qq(psql -t -h 127.0.0.1 -p 6432 -d lcdb -c "UPDATE pgbench_tellers SET filler = 'test' WHERE tid = 1");
print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);

print("success28 = $success28\n");
print("stdout_buf28 = @$stdout_buf28\n");

#
# Confirm replication on Node 2
#

my $cmd29 = qq(psql -t -h 127.0.0.1 -p 6433 -d lcdb -c "SELECT filler FROM pgbench_tellers WHERE tid = 1");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);

print("success29 = $success29\n");
print("stdout_buf29 = @$stdout_buf29\n");
print("If the word test is in @$stdout_buf29 we've proven replication is happening!\n");

my $substring = "test";
if(index($stdout_buf29, $substring) == -1)

{
    exit(0);
}
else
{
    exit(1);
}




