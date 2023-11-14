# This version of the pgEdge installation script is intended to specifically 
# download and test the version of pgEdge that is customer facing.
#

use strict;
use warnings;

use File::Which;
use File::Path;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;

my $cmd = system("curl -fsSL https://pgedge-download.s3.amazonaws.com/REPO/install.py > install.py");
print("cmd = $cmd\n");

my $cmd2 = system("python install.py");
print("cmd2 = $cmd2\n");

if (defined($cmd2))
{
  exit(0);
}
else
{
 exit(1);
}

