
EMAIL="denis@lussier.io"
NAME="denis lussier"
git config --global user.email "$EMAIL"
git config --global user.name "$NAME"
git config --global push.default simple
git config --global credential.helper store
git config --global pull.rebase false

uname=`uname`
uname=${uname:0:7}

if [ $uname == 'Linux' ]; then
  owner_group="$USER:$USER"
  yum --version > /dev/null 2>&1
  rc=$?
  if [ "$rc" == "0" ]; then
    YUM="y"
  else
    YUM="n"
  fi

  if [ "$YUM" == "n" ]; then
    sudo apt install wget curl git python3 openjdk-11-jdk-headless
  fi

  if [ "$YUM" == "y" ]; then
    PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
    if [ "$PLATFORM" == "el8" ]; then
      echo "## $PLATFORM ##"
      yum="dnf -y install"
      sudo $yum epel-release
      sudo dnf config-manager --set-enabled powertools
      sudo $yum wget python39 python39-devel
      sudo $yum java-11-openjdk-devel maven
      sudo dnf -y groupinstall 'development tools'
      sudo $yum zlib-devel bzip2-devel \
        openssl-devel libxslt-devel libevent-devel c-ares-devel \
        perl-ExtUtils-Embed sqlite-devel \
        pam-devel openldap-devel boost-devel 
      sudo $yum curl-devel chrpath clang-devel llvm-devel \
        cmake libxml2-devel 
      sudo $yum libedit-devel 
      sudo $yum *ossp-uuid*
      if [ "$PLATFORM" == "el8" ]; then
        sudo $yum python2 python2-devel
        cd /usr/bin
        sudo ln -fs python2 python
        sudo $yum openjpeg2-devel libyaml libyaml-devel
        sudo $yum ncurses-compat-libs mysql-devel 
	sudo $yum unixODBC-devel protobuf-c-devel libyaml-devel
      fi
      sudo $yum mongo-c-driver-devel freetds-devel systemd-devel
      sudo $yum lz4-devel libzstd-devel krb5-devel
      sudo alternatives --config java
    else
      echo "## ONNLY el8 support"
      exit 1
    fi
  fi

elif [ $uname == 'Darwin' ]; then
  owner_group="$USER:staff"
  if [ "$SHELL" != "/bin/bash" ]; then
    chsh -s /bin/bash
  fi
  brew --version > /dev/null 2>&1
  rc=$?
  if [ ! "$rc" == "0" ]; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew install pkg-config krb5 wget curl readline lz4 openssl@1.1 openldap ossp-uuid

else
  echo "$uname is unsupported"
  exit 1
fi

sudo mkdir -p /opt/pgbin-build
sudo mkdir -p /opt/pgbin-build/pgbin/bin
sudo chown -R $owner_group /opt/pgbin-build
sudo mkdir -p /opt/pgcomponent
sudo chown $owner_group /opt/pgcomponent
mkdir -p ~/dev
cd ~/dev
mkdir -p in
mkdir -p out
mkdir -p history

pip3 --version > /dev/null 2>&1
rc=$?
if [ ! "$rc" == "0" ]; then
  cd ~
  wget https://bootstrap.pypa.io/get-pip.py
  python3 get-pip.py
  rm get-pip.py
fi


aws --version > /dev/null 2>&1 
rc=$?
if [ ! "$rc" == "0" ]; then
  sudo pip3 install awscli
  mkdir -p ~/.aws
  cd ~/.aws
  touch config
  # vi config
  chmod 600 config
fi

cd ~/dev/ndctl
if [ -f ~/.bashrc ]; then
  bf=~/.bashrc
else
  bf=~/.bash_profile
fi
grep NC $bf > /dev/null 2>&1
rc=$?
if [ ! "$rc" == "0" ]; then
  cat bash_profile >> $bf
fi

echo ""
echo "Goodbye!"
