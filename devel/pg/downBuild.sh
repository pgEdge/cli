
## set -x

SPOCK_REPO=spock-private
SPOCK_BRANCH=main

v12=12.19
v13=13.15
v14=14.12
v15=15.7
v16=16.3
v17=17beta1

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
  echoCmd "cd contrib"
  if [ ! -d $SPOCK_REPO ]; then
    echoCmd "git clone https://github.com/pgedge/$SPOCK_REPO"
  fi
  echoCmd "cd $SPOCK_REPO"
  echoCmd "git checkout $SPOCK_BRANCH"
  echoCmd "git pull"
  echoCmd "cd ../.."

  FILES="contrib/$SPOCK_REPO/patches/pg$PGV*"
  for f in $FILES
  do
    echoCmd "patch -p1 -i $f"
  done

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

  patchFromSpock

  makeInstall
  echoCmd "cd .."
}


makeInstall () {
  if [ "$UNAME" = "Darwin" ]; then
    options=""
  else
    ##export LLVM_CONFIG=/usr/bin/llvm-config-64
    ##options="$options --with-openssl --with-llvm --with-gssapi --with-libxml --with-libxslt"
    options="$options --without-openssl --without-readline"
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
PGV=$1
if [ "$PGV" == "12" ]; then
  downBuild $v12
elif [ "$PGV" == "13" ]; then
  downBuild $v13
elif [ "$PGV" == "14" ]; then
  downBuild $v14
elif [ "$PGV" == "15" ]; then
  options="--without-zstd --without-lz4 --without-icu"
  downBuild $v15
elif [ "$PGV" == "16" ]; then
  options="--without-zstd --without-lz4 --without-icu"
  downBuild $v16
elif [ "$PGV" == "17" ]; then
  options="--without-zstd --without-lz4 --without-icu"
  downBuild $v17
else
  echo "ERROR: Incorrect PG version.  Must be between 12 & 17"
  exit 1
fi
 
