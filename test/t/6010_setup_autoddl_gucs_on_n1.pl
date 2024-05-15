# This testcase enables the the two primary auto ddl gucs 
# spock.enable_ddl_replication AND spock.include_ddl_repset
# on node 1 and performs a reload.
#
use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;

# Our parameters are:

my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $host = $ENV{EDGE_HOST};
my $port = $ENV{EDGE_START_PORT};
my $database = $ENV{EDGE_DB};
print("The home directory of node 1 is $homedir1\n");

# command to enable spock.enable_ddl_replication 
my $enableDDLRep = qq(alter system set spock.enable_ddl_replication = on);
# command to enable spock.include_ddl_repset
my $includeDDLRep = qq(alter system set spock.include_ddl_repset = on);
# command to enable spock.allow_ddl_from_functions
my $allowDDLFunc = qq(alter system set spock.allow_ddl_from_functions = on);
# execute the two alter syste commands followed by a server reload
# all commands cannot be combined in a single -c switch
my $cmd1 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $host -p $port -d $database -c "$enableDDLRep" -c "$includeDDLRep" -c "$allowDDLFunc" -c "select pg_reload_conf()");
print("cmd1 = $cmd1\n");
my $stdout_buf= (run_command_and_exit_iferr ($cmd1))[3];
print("stdout_buf = @$stdout_buf\n");
sleep(0.75); #for the reload to be ready

# Validate the two gucs are ON
my $cmd2 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $host -p $port -d $database -c "show spock.enable_ddl_replication" -c "show spock.include_ddl_repset" -c "show spock.allow_ddl_from_functions");
print("cmd2 = $cmd2\n");
my $stdout_buf1= (run_command_and_exit_iferr ($cmd2))[3];
#combining a multi line output into a single line to ensure consistent comparisons to avoid random \n messing up comparisons
@$stdout_buf1 = join(' ', map { sanitize_and_combine_multiline_stdout($_) } @$stdout_buf1);
print("stdout_buf1 = @$stdout_buf1\n");

if (contains($stdout_buf1->[0], "on on on"))
{
    print("AutoDDL Gucs spock.enable_ddl_replication, spock.include_ddl_repset and spock.allow_ddl_from_functions are now enabled");
    exit(0);
}
else
{
    print("One or more of AutoDDL Gucs could not be enabled. Exiting with failure");
    exit(1);
}