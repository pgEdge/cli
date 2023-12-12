use strict;
use warnings;
use JSON;

################################################################################
# writeConfig($data, $fileName)
#
#  Writes the given $data to the named file.
#
#  $data should be a hash (aka dictionary)
#  $fileName should be a string - the given file is overwritten (not appended)
#
#  This function converts the given hash ($data) into JSON form

sub writeConfig
{
    my ($data, $fileName) = @_;

    open my $fh, '>', $fileName or die "can't open output file";
    print($fh encode_json($data));
    close($fh);
}

################################################################################
# readConfig($fileName)
#
#  Reads the JSON string in the given file, converts the JSON into a Perl hash,
#  and returns the hash to the caller.

sub readConfig
{
    my($fileName) = @_;
    
    open(my $fh, '<', $fileName) or die "can't open input file";
    local $/;
    my $jsonString = <$fh>;  # reads the file content into $jsonString
    close($fh);

    my $hashRef = decode_json($jsonString);

    return $hashRef;
}

################################################################################
# Example usage:
#
# my %data = (
#     home_dir   => "/tmp",
#     os         => "GNU/Linux",
#     ip_address => "192.168.187.130",
#     PGDATA     => "/work/PGDATA"
#     );
#
# print("home_dir   = $data{home_dir}\n");
# print("os         = $data{os}\n");
# print("ip_address = $data{ip_address}\n");
# print("PGDATA     = $data{PGDATA}\n");
#
# writeConfig(\%data, '/tmp/config.json');
#
# my $result = readConfig('/tmp/config.json');
#
# print("home_dir   = $result->{home_dir}\n");
# print("os         = $result->{os}\n");
# print("ip_address = $result->{ip_address}\n");
# print("PGDATA     = $result->{PGDATA}\n");
#
# $result->{foo} = 'bar';
#
# print("foo        = $result->{foo}\n");
#
# writeConfig(\%data, '/tmp/config.json');
