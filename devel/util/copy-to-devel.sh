#!/bin/bash
cd "$(dirname "$0")"

export BUCKET=s3://pgedge-devel

if [ "$1" == "" ]; then
  echo "The outDir parameter must be specified"
  exit 1
fi

outDir=$HIST/$1
echo $outDir

if [ ! -d $outDir ]; then
  echo "ERROR: missing $outDir"
  exit 1
fi

sleep 2
cd $outDir
ls
sleep 2

flags="--acl public-read --storage-class STANDARD --recursive"
BR=$BUCKET/REPO
set -x

aws --region $REGION s3 cp . $BR $flags
rc=$?

exit $rc

