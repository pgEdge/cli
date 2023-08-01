# 050_nodectl_start_pg.pl
#
# Starts the cluster; check for running postgres objects with: ps -elf | grep post
# 
#

use strict;
use warnings;

use File::Which;
use PostgreSQL::Test::Cluster;
use PostgreSQL::Test::Utils;
use Test::More tests => 1;
use NodeCtl;
use Try::Tiny;

chdir("./pgedge");

my @args = ("./nodectl", "start", "pg15");

my $result = system(@args);

ok("started");
done_testing();
