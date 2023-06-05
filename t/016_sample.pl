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

my $nc = NodeCtl::get_new_nc("");
my $cmd = qq(psql -h 127.0.0.1 -d postgres -c "CREATE ROLE moo LOGIN PASSWORD 'password'");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= $nc->exec_command($cmd);
diag ("$success");
diag ("$error_message");
diag ("full_buf contains @$full_buf");
diag ("stdout contains @$stdout_buf");
diag ("stderr contains @$stderr_buf");

ok(1);
done_testing();
