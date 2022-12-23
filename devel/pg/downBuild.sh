
## set -x

v12=12.13
v13=13.9
v14=14.6
v15=15.1

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


downBuild () {
  echo " "
  echo "##################### PostgreSQL $1 ###########################"
  echoCmd "rm -rf *$1*"
  echoCmd "wget https://ftp.postgresql.org/pub/source/v$1/postgresql-$1.tar.gz"
  
  if [ ! -d src ]; then
    mkdir src
  fi
  echoCmd "cp postgresql-$1.tar.gz src/."

  echoCmd "tar -xf postgresql-$1.tar.gz"
  echoCmd "mv postgresql-$1 $1"
  echoCmd "rm postgresql-$1.tar.gz"

  echoCmd "cd $1"
  makeInstall
  echoCmd "cd .."
}


makeInstall () {
  brew --version > /dev/null 2>&1
  rc=$?
  if [ "$UNAME" = "Darwin" ] && [ ! "$rc" == "0" ]; then
    echo "ERROR: Darwin requires BREW"
    exit 1
  fi

  if [ "$UNAME" = "Darwin" ]; then
    export LLVM_CONFIG="/opt/homebrew/opt/llvm/bin/llvm-config"
    export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
    export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
  else
    export LLVM_CONFIG=/usr/bin/llvm-config-64
  fi

  options="$options --with-openssl --with-llvm --with-gssapi --with-libxml --with-libxslt"
  ##options="--host=x86_64-w64-mingw32 --without-zlib"
  cmd="./configure --prefix=$PWD $options"
  echo "# $cmd"
  $cmd > config.log
  rc=$?
  if [ "$rc" == "1" ]; then
    exit 1
  fi

  gcc_ver=`gcc --version | head -1 | awk '{print $3}'`
  arch=`arch`
  if [ "$arch" == "aarch64" ] && [ "$gcc_ver" == "10.2.0" ]; then
     export CFLAGS="$CFLAGS -moutline-atomics"
  fi
  echo "# gcc_ver = $gcc_ver,  arch = $arch, CFLAGS = $CFLAGS"

  sleep 1
  cmd="make -j4"
  echoCmd "$cmd"
  sleep 1
  echoCmd "make install"
}


## MAINLINE ##############################

options=""
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
  options="--with-zstd --with-lz4"
  downBuild $v15
else
  echo "ERROR: Incorrect PG version.  Must be between 12 and 15"
  exit 1
fi
 
