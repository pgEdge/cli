
## set -x

v11=11.20
v12=12.15
v13=13.11
v14=14.8
v15=15.3
v16=16beta2

UNAME=`uname`

fatalError () {
  echo "FATAL ERROR!  $1"
  if [ "$2" == "u" ]; then
    printUsageMessage
  fi
  echo
  exit 1
}


echoCmd () {
  echo "# $1"
  checkCmd "$1"
}


checkCmd () {
  $1
  rc=`echo $?`
  if [ ! "$rc" == "0" ]; then
    fatalError "Stopping Script"
  fi
}

patchFromSpock () {
  branch=$1
  patch=$2

  echoCmd "cd contrib"
  echoCmd "git clone https://github.com/pgedge/spock"
  echoCmd "cd spock"
  echoCmd "git checkout $branch"
  echoCmd "cd ../.."
  echoCmd "patch -p1 -i contrib/spock/$patch"

  sleep 10
}


downBuild () {
  echo " "
  echo "##################### PostgreSQL $1 ###########################"
  echoCmd "rm -rf *$1*"
  echoCmd "cp $IN/sources/postgresql-$1.tar.gz ."
  
  if [ ! -d src ]; then
    mkdir src
  fi
  echoCmd "cp postgresql-$1.tar.gz src/."

  echoCmd "tar -xf postgresql-$1.tar.gz"
  echoCmd "mv postgresql-$1 $1"
  echoCmd "rm postgresql-$1.tar.gz"

  echoCmd "cd $1"

  if [ "$pgV" == "15" ]; then
    patchFromSpock REL3_1_STABLE pg15-log_old_value.diff
  elif [ "$pgV" == "16" ]; then
    patchFromSpock REL3_1_STABLE pg16-log_old_value.diff
  fi

  makeInstall
  echoCmd "cd .."
}


makeInstall () {
  ##brew --version > /dev/null 2>&1
  ##rc=$?
  ##if [ "$UNAME" = "Darwin" ] && [ ! "$rc" == "0" ]; then
  ##  echo "ERROR: Darwin requires BREW"
  ##  exit 1
  ##fi

  if [ "$UNAME" = "Darwin" ]; then
    ##export LLVM_CONFIG="/opt/homebrew/opt/llvm/bin/llvm-config"
    ##export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
    ##export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
    ##export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
    options=""
  else
    export LLVM_CONFIG=/usr/bin/llvm-config-64
    options="$options --with-openssl --with-llvm --with-gssapi --with-libxml --with-libxslt"
  fi

  cmd="./configure --prefix=$PWD $options"
  echo "# $cmd"
  $cmd > config.log
  rc=$?
  if [ "$rc" == "1" ]; then
    exit 1
  fi

  if [ `uname` == "Linux" ]; then
    gcc_ver=`gcc --version | head -1 | awk '{print $3}'`
    arch=`arch`
    echo "# gcc_ver = $gcc_ver,  arch = $arch, CFLAGS = $CFLAGS"
    sleep 2
  fi

  cmd="make -j8"
  echoCmd "$cmd"
  sleep 1
  echoCmd "make install"
}


## MAINLINE ##############################

options=""
pgV=$1
if [ "$1" == "11" ]; then
  options=""
  downBuild $v11
elif [ "$1" == "12" ]; then
  options=""
  downBuild $v12
elif [ "$1" == "13" ]; then
  options=""
  downBuild $v13
elif [ "$1" == "14" ]; then
  options=""
  downBuild $v14
elif [ "$1" == "15" ]; then
  options="--with-zstd --with-lz4 --with-icu"
  downBuild $v15
elif [ "$1" == "16" ]; then
  options="--with-zstd --with-lz4 --with-icu"
  downBuild $v16
else
  echo "ERROR: Incorrect PG version.  Must be between 11 and 16"
  exit 1
fi
 
