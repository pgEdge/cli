
echo " "
echo "# run 1a-toolset"
py3V=`python3 --version`
py3M=`echo $py3V | awk '{print $2}' | sed -r 's/([^.]+.[^.]*).*/\1/'`

echo "# py3V = $py3V"
echo "# py3M = $py3M"

um=yum
yum="sudo dnf --skip-broken -y install"
PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
echo "## $PLATFORM ##"

if [ "$PLATFORM" == "el8" ]; then
  $yum -y python39 python39-devel python39-pip gcc-toolset-11
  sudo dnf config-manager --set-enabled powertools
fi

if [ "$PLATFORM" == "el9" ]; then
  $yum python3-devel python3-pip gcc
  sudo dnf config-manager --set-enabled crb
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
  sudo dnf -y remove curl
  $yum curl-devel 
  $yum chrpath clang-devel llvm-devel cmake libxml2-devel 
  $yum libedit-devel
  $yum *ossp-uuid*
  $yum openjpeg2-devel libyaml libyaml-devel
  $yum ncurses-compat-libs systemd-devel
  $yum unixODBC-devel protobuf-c-devel libyaml-devel
  $yum lz4-devel libzstd-devel krb5-devel
  $yum java-17-openjdk-devel

  exit 0
fi


## basic setup for debian based distro's
apt --version
rc=$?
if [ $rc == "0" ]; then
  sudo apt install -y python3-dev python3-pip python3-venv gcc
else
  echo "ERROR: Platform not supported"
  exit 1
fi
 
cd ~
python3 -m venv venv
source ~/venv/bin/activate
 
pip3 install --upgrade pip
