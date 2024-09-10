#!/bin/bash
cd "$(dirname "$0")"

TGZ_REPO="https://pgedge-upstream.s3.amazonaws.com/REPO"
set -e

source env.sh

vers="$1"
pkg="$2"

if [ ! "$pkg" == "" ]; then
  if [ ! "$pkg" == "tgz" ]; then
    echo "# ERROR: package_type \'$pkg\' not supported (must be 'tgz')"
    exit 1
  fi
fi

cmd () {
  echo "# $1"
  $1
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: rc=$rc  Stopping Script"
    exit $rc
  fi

}

## MAINLINE ###################################

if [ "$vers" == "" ] || [ "$vers" == "all" ]; then
  vers="14 15 16 17"
  echo "# default to rebuilding pg \"$vers\""
  cmd "rm -f $OUT/*"
fi

for ver in ${vers}; do
  echo ""
  cmd "rm -f $OUT/*pg$ver*"
  cmd "./build_all.sh $ver"
done

# copy all ctlib versions into OUT
./bp.sh

# remove large ctlib tarballs of different architecture
rm -v $OUT/*ctlibs*osx.tgz
if [ `arch` == "aarch64" ]; then
  rm -v $OUT/*ctlibs*amd.tgz
else
  rm -v $OUT/*ctlibs*arm.tgz
fi

if [ "$pkg" == "tgz" ] && [ "$1" == "all" ]; then
  bndl="pgedge-$hubVV-$OS.tgz"

  cd /tmp

  rm -f $bndl
  rm -rf pgedge

  cp $CLI/install.py /tmp/.
  python3 install.py
  cmd "pgedge/pgedge set GLOBAL REPO $TGZ_REPO"

  cmd "cp -v  $PGE/src/repo/* $OUT/."
  cmd "cp $OUT/* pgedge/data/conf/cache/."

  tar --use-compress-program="pigz -8 --recursive" -cf $bndl pgedge

  rm -f install.py
  rm -rf pgedge

  mv /tmp/$bndl $OUT/.
  ls -lh /$OUT/$bndl
fi

