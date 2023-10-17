# This case tests spock repset-alter.
#


use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# Our parameters are:

my $cmd99 = qq(whoami);
my ($success99, $error_message99, $full_buf99, $stdout_buf99, $stderr_buf99)= IPC::Cmd::run(command => $cmd99, verbose => 0);
print("stdout_buf99 = @$stdout_buf99\n");

my $repuser = "@$stdout_buf99[0]";
my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg16";
my $spock = "3.1";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory from nodectl in json form... 

my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory is {$homedir}\n"); 

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info pg16`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
# print("The port number is {$port}\n");

# Register node 1 and the repset entry on n1: 
print("repuser before chomp = $repuser\n");
chomp($repuser);


# Create a new replication set to modify:

my $cmd31 = qq($homedir/nodectl spock repset-create my_new_repset lcdb);
print("cmd31 = $cmd31\n");
my ($success31, $error_message31, $full_buf31, $stdout_buf31, $stderr_buf31)= IPC::Cmd::run(command => $cmd31, verbose => 0);

if(!(contains(@$stdout_buf31[0], "repset_create")))
{
    exit(1);
}

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd33 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd33 = $cmd33\n");
my($success33, $error_message33, $full_buf33, $stdout_buf33, $stderr_buf33)= IPC::Cmd::run(command => $cmd33, verbose => 0);

if(!(contains(@$stdout_buf33[0], "my_new_repset       | t                | t                | t                | t")))
{
    exit(1);
}

# We'll leave off the database name to check the error with the repset-alter command...

my $cmd32 = qq($homedir/nodectl spock repset-alter my_new_repset);
print("cmd32 = $cmd32\n");
my ($success32, $error_message32, $full_buf32, $stdout_buf32, $stderr_buf32)= IPC::Cmd::run(command => $cmd32, verbose => 0);

if(!(contains(@$stderr_buf32[0], "ERROR")))
{
    exit(1);
}

# We'll alter the repset now, so it doesn't accept DELETE statements...

my $cmd34 = qq($homedir/nodectl spock repset-alter my_new_repset lcdb --replicate_delete=false);
print("cmd34 = $cmd34\n");
my ($success34, $error_message34, $full_buf34, $stdout_buf34, $stderr_buf34)= IPC::Cmd::run(command => $cmd34, verbose => 0);

if(!(contains(@$full_buf34[0], "repset_alter")))
{
    exit(1);
}

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd35 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd35 = $cmd35\n");
my($success35, $error_message35, $full_buf35, $stdout_buf35, $stderr_buf35)= IPC::Cmd::run(command => $cmd35, verbose => 0);

if(!(contains(@$stdout_buf35[0], "my_new_repset       | t                | t                | f                | t")))
{
    exit(1);
}


# We'll alter the repset now, so it doesn't accept INSERT statements...

my $cmd36 = qq($homedir/nodectl spock repset-alter my_new_repset lcdb --replicate_insert=false);
print("cmd36 = $cmd36\n");
my ($success36, $error_message36, $full_buf36, $stdout_buf36, $stderr_buf36)= IPC::Cmd::run(command => $cmd36, verbose => 0);

if(!(contains(@$full_buf36[0], "repset_alter")))
{
    exit(1);
}

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd37 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd37 = $cmd37\n");
my($success37, $error_message37, $full_buf37, $stdout_buf37, $stderr_buf37)= IPC::Cmd::run(command => $cmd37, verbose => 0);

if(!(contains(@$stdout_buf37[0], "my_new_repset       | f                | t                | t                | t")))
{
    exit(1);
}


# We'll alter the repset now, so it doesn't accept UPDATE statements...

my $cmd38 = qq($homedir/nodectl spock repset-alter my_new_repset lcdb --replicate_update=false);
print("cmd38 = $cmd38\n");
my ($success38, $error_message38, $full_buf38, $stdout_buf38, $stderr_buf38)= IPC::Cmd::run(command => $cmd38, verbose => 0);

if(!(contains(@$full_buf38[0], "repset_alter")))
{
    exit(1);
}


# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd39 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd39 = $cmd35\n");
my($success39, $error_message39, $full_buf39, $stdout_buf39, $stderr_buf39)= IPC::Cmd::run(command => $cmd39, verbose => 0);

if(!(contains(@$stdout_buf39[0], "my_new_repset       | t                | f                | t                | t")))
{
    exit(1);
}


# We'll alter the repset now, so it doesn't accept TRUNCATE statements...

my $cmd40 = qq($homedir/nodectl spock repset-alter my_new_repset lcdb --replicate_truncate=false);
print("cmd40 = $cmd40\n");
my ($success40, $error_message40, $full_buf40, $stdout_buf40, $stderr_buf40)= IPC::Cmd::run(command => $cmd40, verbose => 0);

if(!(contains(@$full_buf40[0], "repset_alter")))
{
    exit(1);
}

# Then, use the info to connect to psql and test for the existence of the replication set.

my $cmd41 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set");
print("cmd41 = $cmd41\n");
my($success41, $error_message41, $full_buf41, $stdout_buf41, $stderr_buf41)= IPC::Cmd::run(command => $cmd41, verbose => 0);

if(!(contains(@$stdout_buf41[0], "my_new_repset       | t                | t                | t                | f")))

{
    exit(1);
}

# Lines 124 through 129 of the test case table
   
# Then, connect to psql and create a table:

my $cmd42 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "CREATE TABLE bar (name VARCHAR(40), amount INTEGER, pkey INTEGER PRIMARY KEY)");
print("cmd42 = $cmd42\n");
my($success42, $error_message42, $full_buf42, $stdout_buf42, $stderr_buf42)= IPC::Cmd::run(command => $cmd42, verbose => 0);

if(!(contains(@$stdout_buf42[0], "CREATE TABLE")))

{
    exit(1);
}

# Invoke: ./nc spock repset-add-table with a missing dbname.

my $cmd43 = qq($homedir/nodectl spock repset-add-table my_new_repset bar);
print("cmd43 = $cmd43\n");
my ($success43, $error_message43, $full_buf43, $stdout_buf43, $stderr_buf43)= IPC::Cmd::run(command => $cmd43, verbose => 0);

if(!(contains(@$full_buf43[0], "ERROR")))
{
    exit(1);
}


# Invoke: ./nc spock repset-add-table demo_rep_set pgbench_accounts demo --columns='column_names' with a non-existent column name.

my $cmd44 = qq($homedir/nodectl spock repset-add-table my_new_repset bar lcdb --columns='nosuchcolumn');
print("cmd44 = $cmd44\n");
print("I'm not sure that this command should add the non-existent column to the replication set; I've asked, and am waiting for an answer.\n");
my ($success44, $error_message44, $full_buf44, $stdout_buf44, $stderr_buf44)= IPC::Cmd::run(command => $cmd44, verbose => 0);

# We need to use psql to check the result for certain:

my $cmd45 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set_table");
print("cmd45 = $cmd45\n");
my($success45, $error_message45, $full_buf45, $stdout_buf45, $stderr_buf45)= IPC::Cmd::run(command => $cmd45, verbose => 0);

if(contains(@$stdout_buf45[0], "bar"))
{
    exit(1);
}

# Invoke: ./nc spock repset-add-table demo_rep_set pgbench_accounts demo --columns='column_names' correctly

my $cmd46 = qq($homedir/nodectl spock repset-add-table my_new_repset bar lcdb --columns='pkey,amount');
print("cmd46 = $cmd46\n");
my ($success46, $error_message46, $full_buf46, $stdout_buf46, $stderr_buf46)= IPC::Cmd::run(command => $cmd46, verbose => 0);

# We need to use psql to check the result for certain:

my $cmd47 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM spock.replication_set_table");
print("cmd47 = $cmd47\n");
my($success47, $error_message47, $full_buf47, $stdout_buf47, $stderr_buf47)= IPC::Cmd::run(command => $cmd47, verbose => 0);

if(contains(@$full_buf47[0], "{pkey,amount}"))
{
    exit(0);
}
else
{
    exit(1);
}





