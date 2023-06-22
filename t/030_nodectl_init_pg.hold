# 030_nodectl_init_pg.pl
#
# This test initializes the database cluster by invoking initdb; the server is not running.
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

my @args = ("./nodectl", "init", "pg15", "-U", "admin", "-P", "password", "-d", "demo" );

my $nc = NodeCtl::get_new_nc("/tmp/nodectl_dir");

my $result = system(@args);

my $datadir = $nc->get_data_dir();

if (-d "$datadir")
{
    ok(1, "Initialized");
}
else
{
    ok(0, "initdb failed");
}

done_testing();
