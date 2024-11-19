#!/bin/bash
cd "$(dirname "$0")"

TGZ_REPO="https://pgedge-download.s3.amazonaws.com/REPO"

source env.sh

set -ex

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
cmd "cp $HIST/out_old/* $cache/."

cmd "cp -r $DEVEL/packages $cache/."
cmd "python3 pgedge/hub/scripts/get_old.py"

echo "RUNNING pigz..."
tar --use-compress-program="pigz -8 --recursive" -cf $bndl pgedge

rm -f install.py
rm -rf pgedge

mv /tmp/$bndl $OUT/.
ls -lh /$OUT/$bndl

