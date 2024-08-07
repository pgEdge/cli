#!/bin/bash
cd "$(dirname "$0")"

if [ "$IN" == "" ]; then
  echo "ERROR: Missing \$IN environment variable"
  exit 1
fi

mkdir -p $IN
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: Couldn't make $IN directory"
  exit 1
fi

pull=in/pull-s3.sh
if [ ! -f "$pull" ]; then
  echo "ERROR: missing pull file \"$pull\""
  exit 1
fi

cp $pull $IN/.
cd $IN
./pull-s3.sh
chmod 755 *.sh

cd ~/dev
mkdir -p out
mkdir -p history

