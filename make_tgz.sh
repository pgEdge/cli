#!/bin/bash
cd "$(dirname "$0")"

TGZ_REPO="https://pgedge-upstream.s3.amazonaws.com/REPO"
set -ex

source env.sh

vers="$1"
rebuild_flag="$2"
tgz_flag="$3"

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

if [ "$rebuild_flag" == "y" ]; then
  if [ "$vers" == "" ] || [ "$vers" == "all" ]; then
    vers="15 16 17"
    echo "# default to rebuilding pg \"$vers\""
    cmd "rm -f $OUT/*"
  fi

  for ver in ${vers}; do
    echo ""
    cmd "rm -f $OUT/*pg$ver*"
    cmd "./build_all.sh $ver"
  done
fi

# copy all ctlib versions into OUT
./bp.sh

# remove large ctlib tarballs of different architecture
if [ `arch` == "aarch64" ]; then
  rm -f $OUT/*ctlibs*amd.tgz
else
  rm -f $OUT/*ctlibs*arm.tgz
fi

bndl="pgedge-$hubVV-$OS.tgz"

cd /tmp

rm -f $bndl
rm -rf pgedge

cp $CLI/install.py /tmp/.
python3 install.py
cmd "pgedge/pgedge set GLOBAL REPO $TGZ_REPO"

cache=pgedge/data/conf/cache
cmd "cp -v  $PGE/src/repo/* $OUT/."
cmd "cp $OUT/* $cache/."

cmd "cp -r $DEVEL/packages $cache/."

if [ ! "tgz_flag" == "y" ]; then
  echo ""
  echo "############ NOT running pigz ################"
  echo ""
  exit 0
else
  echo "RUNNING pigz..."
fi

tar --use-compress-program="pigz -8 --recursive" -cf $bndl pgedge

rm -f install.py
rm -rf pgedge

mv /tmp/$bndl $OUT/.
ls -lh /$OUT/$bndl

