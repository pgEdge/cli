# 020_nodectl_install_pg.pl
#
# Prove that nodectl install pg15 will download and install PG 15.
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

my @args = ("./nodectl", "install", "pg15");

my $result = system(@args);

if ($result != 0)
{
    ok(0, "install failed");
}
else
{
    ok(1, "install complete");
}

done_testing();
