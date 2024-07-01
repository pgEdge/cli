
echo " "
echo "# run 1a-toolset"

yum="sudo dnf -y install"
PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
echo "## $PLATFORM ##"

if [ "$PLATFORM" == "el8" ]; then
  sudo yum remove -y python3
  $yum python39 python39-devel python39-pip gcc-toolset-12
  sudo dnf config-manager --set-enabled powertools
  $yum @ruby:3.0
fi

if [ "$PLATFORM" == "el9" ]; then
  $yum python3-devel python3-pip gcc
  sudo dnf config-manager --set-enabled crb
  sudo yum install ruby
fi

if [ "$PLATFORM" == "el8" ] || [ "$PLATFORM" == "el9" ]; then
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

  $yum podman podman-docker podman-compose

  rm -f install-rust.sh
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install-rust.sh 
  chmod 755 install-rust.sh
  ./install-rust.sh -y
  rm install-rust.sh

fi


apt --version > /dev/null 2>&1
rc=$?
if [ $rc == "0" ]; then
  apt="sudo apt-get install -y"
  $apt python3-dev python3-pip python3-venv gcc

  $apt ruby squashfs-tools
  gem install fpm
fi

sudo update-alternatives --set python3 /usr/bin/python3.9
 
cd ~
python3 -m venv venv
source ~/venv/bin/activate
 
pip3 install --upgrade pip
