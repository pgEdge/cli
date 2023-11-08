#!/bin/bash
cd "$(dirname "$0")"

export BUCKET=s3://pgedge-upstream

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
cmd="aws --region $REGION s3 cp . $BUCKET/REPO $flags"
echo $cmd
sleep 3

$cmd
rc=$?
echo "rc=($rc)"
exit $rc

