
## set -x

SPOCK_REPO=spock-private

v12=12.18
v13=13.14
v14=14.11
v15=15.6
v16=16.2
v17=17devel

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
  if [ ! -d $SPOCK_REPO ]; then
    echoCmd "git clone https://github.com/pgedge/$SPOCK_REPO"
  fi
  echoCmd "cd $SPOCK_REPO"
  echoCmd "git checkout $branch"
  echoCmd "git pull"
  echoCmd "cd ../.."
  echoCmd "patch -p1 -i contrib/$SPOCK_REPO/$patch"

  sleep 2
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

  if [ "$pgV" == "14" ] || [ "$pgV" == "15" ] || [ "$pgV" == "16" ] || [ "$pgV" == "17" ]; then
    patchFromSpock main patches/pg$pgV-005-log_old_value.diff
  fi

  if [ "$pgV" == "16" ]; then
    patchFromSpock main patches/pg$pgV-012-hidden_columns.diff
    patchFromSpock main patches/pg$pgV-015-delta_apply_function.diff
  fi

  makeInstall
  echoCmd "cd .."
}


makeInstall () {
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
if [ "$1" == "12" ]; then
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
elif [ "$1" == "17" ]; then
  options="--with-zstd --with-lz4 --with-icu"
  downBuild $v17
else
  echo "ERROR: Incorrect PG version.  Must be between 12 & 17"
  exit 1
fi
 
