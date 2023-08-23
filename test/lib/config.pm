use strict;
use warnings;
use JSON;
use Data::Dumper;

sub writeConfig
{
    my ($data, $fileName) = @_;

    open my $fh, '>', $fileName or die "can't open output file";

    print($fh encode_json($data));
    
    close($fh);    
}

sub readConfig
{
    my($fileName) = @_;
    
    open(my $fh, '<', $fileName) or die "can't open input file";

    local $/;

    my $jsonString = <$fh>;  # reads the file content into $jsonString

    close($fh);

    my $hashRef = decode_json($jsonString);

#    return decode_json($jsonString);

    print("type of hashRef is " . ref($hashRef) . "\n");
    print(Dumper($hashRef) . "\n");
    
    return $hashRef;
}

my $home = $ENV{HOME};

print("HOME = $home\n");
print("old pwd = $ENV{OLDPWD}\n");

my %data = (
    home_dir   => "/tmp",
    os         => "GNU/Linux",
    ip_address => "192.168.187.130",
    PGDATA     => "/work/PGDATA"
    );

print("home_dir   = $data{home_dir}\n");
print("os         = $data{os}\n");
print("ip_address = $data{ip_address}\n");
print("PGDATA     = $data{PGDATA}\n");

writeConfig(\%data, '/tmp/config.json');

my $result = readConfig('/tmp/config.json');

printf "reftype:%s\n", ref($result);

print("home_dir   = $result->{home_dir}\n");
print("os         = $result->{os}\n");
print("ip_address = $result->{ip_address}\n");
print("PGDATA     = $result->{PGDATA}\n");

$result->{foo} = 'bar';

print("foo        = $result->{foo}\n");
