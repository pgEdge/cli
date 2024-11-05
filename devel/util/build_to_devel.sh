#!/bin/bash
cd "$(dirname "$0")"

PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`

cmd () {
  echo "# $1"
  $1
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: rc=$rc  Stopping Script"
    exit $rc
  fi

}

step () {
  echo ""
  echo "## step $1 - $2"
}


step 0 "## initialization  #######################"
export BUCKET=s3://pgedge-devel
echo "#  BUCKET = $BUCKET"

now=`date '+%F %r %Z'`
echo "#     now = $now"

run_day=`date +%j`
echo "# run_day = $run_day"

vers=$1
echo "#     vers = \"$vers\""


if [ ! "$#" == "1" ]; then
  echo "ERROR: One parm must be specified such as '15 16'"
  exit 1
fi

if [ "$vers" == "" ]; then
   echo "ERROR: Parm 1 must be space delimited string of versions"
   exit 1
fi

step 1 "cleanup any old ########################"
outDir=$HIST/devel-$run_day
cmd "rm -rf $outDir"
cmd "mkdir $outDir"
cmd "rm -f $OUT/*"

step 2 "get latest cli #########################"
cmd "cd $PGE"
cmd "git status"
cmd "git pull"

step 3a "building $vers #########################"
./make_tgz.sh  "$vers" y y

step 4 "copy OUT to HIST (outDir) #############"
cmd "cp $OUT/* $outDir"
cmd "cd $outDir"
cmd "ls"
sleep 3

step 5 "copy to S3 ############################"
flags="--acl public-read --storage-class STANDARD --recursive"
cmd "aws --region $REGION s3 cp . $BUCKET/REPO $flags"

step 6 "Goodbye! ##############################"
exit 0

