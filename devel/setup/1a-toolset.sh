
echo " "
echo "# run 1a-toolset"


install_rust () {
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs/ | sh -s -- --default-toolchain=1.79.0 -y
}


install-apt-toolset () {
  $apt podman podman-compose
  $apt ruby squashfs-tools
  sudo gem install fpm

  $apt build-essential flex bison libxml2 libxslt-dev
  $apt systemtap-sdt-dev clang pkg-config liblz4-dev libzstd-dev
  $apt libreadline-dev libssl-dev uuid-dev libipc-run-perl

  $apt libclang-dev libopenblas-dev libz-dev tzdata lld llvm-dev
  $apt libxgboost-dev cmake

  install_rust
}


yum="sudo dnf -y install"
apt="sudo apt-get install -y"
PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
echo "## $PLATFORM ##"

if [ "$PLATFORM" == "el8" ]; then
  sudo dnf config-manager --set-enabled powertools
  $yum @ruby:3.0
fi

if [ "$PLATFORM" == "el9" ]; then
  sudo dnf config-manager --set-enabled crb
  $yum ruby
fi

if [ "$PLATFORM" == "el8" ] || [ "$PLATFORM" == "el9" ]; then
  $yum python39 python39-devel python39-pip gcc-toolset-13
  $yum git net-tools wget curl pigz sqlite which zip

  $yum cpan
  echo yes | sudo cpan FindBin
  sudo cpan IPC::Run

  $yum epel-release

  sudo dnf -y groupinstall 'development tools'
  sudo dnf -y --nobest install zlib-devel bzip2-devel lbzip2 \
      openssl-devel libxslt-devel libevent-devel c-ares-devel \
      perl-ExtUtils-Embed pam-devel openldap-devel boost-devel
  $yum curl-devel 
  $yum chrpath clang-devel llvm-devel cmake libxml2-devel 
  $yum libedit-devel
  $yum *ossp-uuid*
  $yum openjpeg2-devel libyaml libyaml-devel
  $yum ncurses-compat-libs systemd-devel
  $yum unixODBC-devel protobuf-c-devel libyaml-devel
  $yum lz4-devel libzstd-devel krb5-devel

  $yum geos-devel proj-devel gdal

  $yum sqlite-devel

  $yum rpm-build squashfs-tools
  gem install fpm

  $yum podman podman-compose

  install_rust

  sudo update-alternatives --set python3 /usr/bin/python3.9
fi


apt --version > /dev/null 2>&1
rc=$?
if [ $rc == "0" ]; then
  $apt python3-dev python3-pip python3-venv gcc sqlite3 sudo

  #install-apt-toolset
fi
 
cd ~
python3 -m venv venv
source ~/venv/bin/activate
 
pip3 install --upgrade pip
