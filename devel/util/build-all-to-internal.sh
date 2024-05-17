#!/bin/bash
cd "$(dirname "$0")"

export BUCKET=s3://pgedge-internal
run_day=`date +%j`

cmd () {
  echo ""
  echo "# $1"
  $1
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: rc=$rc  Stopping Script"
    exit $rc
  fi

}


##  MAINLINE ##########################################
outDir=$HIST/internal-$run_day
cmd "rm -rf $outDir"
cmd "mkdir $outDir"

cmd "cd $PGE"
cmd "git pull"
cmd "rm -f $OUT/*"
cmd "./build_all.sh 14"

cmd "cp $OUT/* $outDir"
cmd "cd $outDir"
cmd "ls"
sleep 3

flags="--acl public-read --storage-class STANDARD --recursive"
BR=$BUCKET/REPO

cmd "aws --region $REGION s3 cp . $BR $flags"

exit 0

