# 040_nodectl_config_pg15.pl
# 
# By the time we invoke this command, the database cluster has been initialized and the server isn't running.
# 
# You can set parameter variables at this point in the test sequence (just perform tests 020/030 first).

use strict;
use warnings;

use File::Which;
use PostgreSQL::Test::Cluster;
use PostgreSQL::Test::Utils;
use Test::More tests => 1;
use NodeCtl;
use Try::Tiny;

chdir("./pgedge");

my @args = ("./nodectl", "config", "pg15", "-p", "5432");

my $result = system(@args);

ok("configured");
done_testing();
