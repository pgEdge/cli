package NodeCtl;

use strict;
use warnings;
use lib;
use Test::More;
use WWW::Curl::Simple;
use base ("PostgreSQL");
use File::Temp qw/ tempfile tempdir /;
use File::Path qw(make_path remove_tree);
use File::Find;
use File::Finder;
use JSON;

our (@all_nodes);

our @EXPORT = qw(
    get_new_nc
    get_info_item_pg15
    get_home_dir
    get_data_dir
    path
    findExecutable
    downloadInstaller
    );

################################################################################
# execute
#
#  Executes a command at the shell prompt.
#
#  NOTE: This will return the output from a given command.
#

sub execute
{
    my ($self, $cmd) = @_;

    my $raw = `$cmd`;
    
        diag("inside execute, cmd = $cmd, raw = $raw");
    # return ("hello", 42);
    return ($raw, ${^CHILD_ERROR_NATIVE});
}

    
################################################################################
# exec_command
#
# Invokes a command at the shell prompt.
#
# This function invokes a command and returns a result and buffer info. The 
# function expects an argument ($cmd) that contains connection information and the
# command it will invoke.
#
# The result of the command is returned in the following variables: $success, $error_message,
# $full_buf, $stdout_buf, $stderr_buf.
#
# You can use code similar to the following to call exec_command:
#
#     my $nc = NodeCtl::get_new_nc("");
#     my $cmd = "psql -h 127.0.0.1 -d postgres -c 'CREATE DATABASE database_name'";
#     my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= $nc->exec_command($cmd);
# 
# If you need to quote a string-identifier, use \":
#     "psql -h 127.0.0.1 -d postgres -c 'CREATE ROLE \"Foo\"'";
# Leave simple identifiers unquoted:
#     "psql -h 127.0.0.1 -d postgres -c 'CREATE ROLE foo'";
#
# You may find this page helpful:
#    https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
#
# $success and $error_message may be undefined values. You can check as follows:
#
#    if ($success)
#    {
#        diag("success is TRUE\n");
#    }
#    else
#    {
#        diag("success is FALSE\n");
#    }
# 
#    if (defined($error_message))
#    {
#        diag("error message = $error_message\n");
#    }
#    else
#    {
#        diag("no error reported\n");
#    }#
#

sub exec_command
{   

    my ($self, $cmd) = @_;
    
    my ( $success, $error_message, $full_buf, $stdout_buf, $stderr_buf ) = IPC::Cmd::run( command => $cmd, verbose => 0 );
   
    return ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf);

}

#################################################################################
# get_new_nc
#
#  This function will create and return a new NodeCtl object.
#
#  Support for $path is deprecated

sub get_new_nc
{
    my ($path) = @_;
    my $result = new NodeCtl($path);

    return $result;
}

################################################################################
# new
#
#  This is the constructor for a NodeCtl object.
#
#  At the moment, this function expects a single argument ($path) and we store
#  that string in the object that we are building.
#
#  Support for $path is deprecated.

sub new
{
    my ($class, $path) = @_;
    
    my $self = {
	_path => $path
    };
    
    bless $self, $class;

    return $self;
}

################################################################################
# get_info_item_pg15
#
#  Returns the value of the given $item found in the
#  output from "nc info pg15".
#
#  NOTE: this function must be called from a $nc object, for example:
#            my $result = $nc->get_info_item_pg15();

sub get_info_item_pg15
{
    my ($self, $item) = @_;

    my $home_dir = $self->get_home_dir();

    my $cmd = $self->get_home_dir() . "/nc --json info pg15";
    my $raw = `$cmd`;
    my $out = decode_json(`$cmd`);
    
    return $out->[0]->{$item};
}

################################################################################
# get_home_dir
#
#   Returns the "home" directory as exposed by the
#   "nc info" command.

sub get_home_dir
{
    my ($self) = @_;

    my $raw = `./nc --json info`;
    my $out = decode_json(`./nc --json info`);
    
    return $out->[0]->{"home"};
}

################################################################################
# get_data_dir
#
#   Returns the $PGDATA directory name

sub get_data_dir
{
    my ($self) = @_;

    return $self->get_info_item_pg15("datadir");
}


sub path
{
    my ($self) = @_;

    return $self->{_path};
    
}

################################################################################
# findExecutable
#
#  Given the name of an executable, returns the pathname of that executable as
#  found by searching $PATH

sub findExecutable
{
    my ($self, $exeName) = @_;

    my $exePath = scalar File::Which::which($exeName);

    return $exePath;
}

=pod
= item $nc->downloadInstaller(url)

Download the nodectl installer from the given url

    url:  URL of the file to download

    Returns: the content of the URL

=cut

sub install
{
    my ($self, $url) = @_;

    $self->waitForUser("about to downloadInstaller ($url)");
    
    my $content = $self->downloadInstaller($url);

    $self->waitForUser("installer downloaded, about to destroyWorkspace");

    $self->destroyWorkspace();

    $self->waitForUser("workspace destroyed, about to runInstaller (python installer.py)");
    
    $self->runInstaller($content);

    $self->waitForUser("runInstaller complete - copy /tmp/cli.py to pgedge/hub/scripts and press Return");
}

sub installPGEdge
{
    my ($self, %params) = @_;

    my $download = $params{download};
    my $password = $params{password};
    my $username = $params{username};
    my $database = $params{database};

    # system("echo 'installPGEdge' >> /tmp/nc.log");
    # system("echo -n 'pwd ' >> /tmp/nc.log && pwd >> /tmp/nc.log");
    chdir("./pgedge");
    # system("echo -n 'pwd after chdir' >> /tmp/nc.log && pwd >> /tmp/nc.log");
    # system("ls >> /tmp/nc.log");

    $self->waitForUser("installPGEdge - about to exec ./nodectl install pgedge");
    
    my @args = ("./nodectl", "install", "pgedge", "-U", $username, "-P", $password, "-d", $database);

    my $result = system(@args);

    # system("nodectl install returned");
    # system("ls >> /tmp/nc.log");
}

################################################################################
# downloadInstaller
#
#   Given a URL, this function downloads the data found at that address and
#   returns the content.

sub downloadInstaller
{
    my ($self, $url) = @_;

    $self->waitForUser("inside of downloadInstaller " . $url);
    
    my $curl = WWW::Curl::Simple->new();
    my $res = $curl->get($url);

    return $res->content;
}

################################################################################
# runInstaller
#
#  Runs a given python3 program ($content) and returns the exit code from the
#  python interpreter.  In general, an exit code of 0 indicates success and any
#  other exit code is likely to indicate an error.

sub runInstaller
{
    my ($self, $content) = @_;
    my @args = ("python3", "-c", $content);

    return system(@args);
}

################################################################################
# destroyWorkspace
#
#    Removes ./pgedge and ./data/pg15 directory trees
#
#    FIXME: the actual directory names should be fetched from "./nc info" and
#           "./nc info pg15" commands.

sub destroyWorkspace
{
    my ($self) = @_;
    my $cwd = Cwd::getcwd();
    my @dirs = ("$cwd/pgedge", "$cwd/data/pg15");

    $self->waitForUser("about to remove_tree");
    
    File::Path::remove_tree(@dirs);

    $self->waitForUser("remove_tree complete");    
}

sub startPostmaster
{
    my ($self, %params) = @_;

    my $password = $params{password};
    my $username = $params{username};
    my $database = $params{database};

    diag("password = $password");
    diag("username = $username");
    diag("database = $database");
    
    chdir("./pgedge");
    $self->waitForUser("changed to ./pgedge");

    my @args = ("./nodectl", "install", "pgedge", "-U", $username, "-P", $password, "-d", $database);

    $self->waitForUser("calling system(" . join(",", @args). ")");
    
    my $result = system(@args);

    $self->waitForUser("startPostmaster - system returned " . $result);
}

################################################################################
# waitForUser
#
#    Prints the given prompt to stdout and waits for the user to press the enter
#    key.  This function returns any text entered by the user.
#
#    NOTE: this function is intended for debugging and should not be invoked by
#          an actual test script.

sub waitForUser
{
    my ($self, $prompt) = @_;

    diag("**$prompt");

    # Enable one of the two following statements.  If you want the test
    # to pause until the user presses enter, uncomment the next line; if
    # you want to simply display the given prompt, uncomment the second
    # line (and comment out the first line).

    #my $reply = <STDIN>;
    my $reply = "";
    
    chomp($reply);

    return $reply;
}

################################################################################
# INIT
#
#  This "function" can be used to initialize the NodeCtl.pm module (not a $nc
#  object)

INIT
{
    # place any necessary module initialization code here
}

1;

