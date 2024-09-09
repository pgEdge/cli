#!/bin/bash
cd "$(dirname "$0")"

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
#  cmd "rm -f $OUT/*"
fi

for ver in ${vers}; do
  echo ""
#  cmd "rm -f $OUT/*pg$ver*"
#  cmd "./build_all.sh $ver"

done

./devel/startHTTP.sh
set -x

if [ "$pkg" == "tgz" ] && [ "$1" == "all" ]; then

  bndl="pgedge-$hubV-$OS.tgz"

  cd /tmp

  rm -f $bndl
  rm -rf pgedge

  cp $CLI/install.py /tmp/.
  python3 install.py

  cmd "cp $OUT/* pgedge/data/conf/cache/."

  ##cmd "tar czf $bndl pgedge"
  ##cmd "tar cf - pgedge | pigz -f $bndl"
  tar --use-compress-program="pigz -6 --recursive" -cf $bndl pgedge

  rm -f install.py
  rm -rf pgedge

  ls -lh /tmp/$bndl
fi

