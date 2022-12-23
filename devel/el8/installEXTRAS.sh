install="sudo dnf install -y"

## for PLV8
$install gcc-toolset-11-build
$install gcc-toolset-11-libatomic-devel
$install glib2-devel
$install ninja-build

## for NGINX
$install perl-Pod-Html

## for MOSQUITTO
$install cjson-devel

## for POSTGIS
$install proj proj-devel
$install geos geos-devel
$install gdal gdal-devel

#source /opt/rh/gcc-toolset-11/enable
