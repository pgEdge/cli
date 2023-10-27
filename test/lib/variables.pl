# These are sample variables and a test case that you can run at the command line with the command: perl t/test.pl
# 
# Before using environment variables, either set them with an EXPORT statement at the command line:
#
# export EDGE_PATH_TO_N1=/home/susan/work/nodectl/test/new_directory_from_ENV
# or
# source t/lib/config.env
#
# If you need to add another multi-use variable, add it first to config.env, then to edge.pm.  Don't forget 
# to source your variables again before you try to use them!
# 
# Right now, we're using all of these use statements.  I'll try to get them out to a file next:

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

# This is how to use a single-use variable in a script:

my $variable = "single_use";

print("This is a $variable variable\n");

# These commands will pull an environment variable; :

print ("$ENV{PATH};\n");
print("n1   = $ENV{EDGE_N1}\n");
print("password = $ENV{EDGE_PASSWORD}\n");
print("username = $ENV{EDGE_USERNAME}\n");

IPC::Cmd::run(command => qq(mkdir -p $ENV{EDGE_N1}), verbose => 0);

# This command (works, and) prints out all of the pgEdge environment variables:
# declared in config.env and the edge.pm module:
 
foreach (sort keys %ENV) {
#    where ENV contains EDGE_ - look for selecting a regex from Env
    next if $_ !~ "^EDGE_*";
    print "$_  =  $ENV{$_}\n";
}


1;
