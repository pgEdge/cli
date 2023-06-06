#!/usr/bin/perl

use strict;
use warnings;
use IPC::Cmd qw(run);
use 5.010;
use strict;
use warnings;

use File::Which;
use PostgreSQL::Test::Cluster;
use PostgreSQL::Test::Utils;
use NodeCtl;
use Test::More tests => 1;
use Try::Tiny;

chdir("./pgedge");

my $nc = NodeCtl::get_new_nc("");
#my $cmd = qq(./nodectl spock node-create n1 'host=127.0.0.1 user=pgedge dbname=demo' demo);

my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= $nc->get_bin_dir();

diag ("The bin directory is at: @$full_buf");

ok(1);
done_testing();
