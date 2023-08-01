# 020_nodectl_install_pg.pl
#

use strict;
use warnings;

use File::Which;
use File::Path;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

my $cmd = system("python install.py");
print("cmd = $cmd\n");

if (defined($cmd))
{
  exit(0);
}
else
{
 exit(1);
}

