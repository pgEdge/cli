# This test case runs the command:
# ./nodectl cluster create-local demo 2 --pg 15
#
# We also query ./nodectl --json info pg15 to confirm the version of the running instance.
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
# First, we use nodectl to create a two-node cluster named demo; the nodes are named n1/n2 (default names), 
# the database is named lcdb (default), and it is owned by lcdb (default). At this point, lcdb is not added
# to the .pgpass file.
# 

my $cmd = qq(./nodectl cluster create-local demo 2 --pg 15);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);

#
# Print statements
#

print("full_buf = @$full_buf\n");
print("stderr_buf = @$stderr_buf\n");

print("This s/b a 2 node cluster named demo, owned by lcdb, with a db named lcdb.  The nodes are named n1/n2.\n");
print("Right now, they're running on 6432 and 6433\n");

#
# Then, we retrieve the Postgres version (the component) number from nodectl in json form... 
# this is to catch cases where more than one copy of Postgres is running.
#
my $json = `./nc --json info pg15`;
my $out = decode_json($json);
my $component = $out->[0]->{"component"};
print("The cluster is running = {$component}\n");

if ($component eq "pg15")
{
    exit(0);
}
else
{
    exit(1);
}

