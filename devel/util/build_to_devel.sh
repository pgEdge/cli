#!/bin/bash
cd "$(dirname "$0")"

source $PGE/env.sh
# offline tgz bundle name
offline_tgz_bndl="pgedge-$hubVV-$OS.tgz"

cmd () {
  echo "# $1"
  eval "$1"  # Use eval to properly handle nested quotes
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

vers="15 16 17"
cleaner="$1"
echo "#     vers = \"$vers\""

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

step 3a "building tgz bundle ####################"
./make_tgz.sh

# Verify that the offline tarball was created
if [ ! -f "$OUT/$offline_tgz_bndl" ]; then
    echo "ERROR: make_tgz.sh did not generate expected tarball: $offline_tgz_bndl"
    exit 1
fi

step 4 "copy OUT to HIST (outDir) #############"
cmd "cp $OUT/* $outDir"
cmd "cd $outDir"
cmd "ls"
sleep 3

step 5 "check if cleanup S3 ###################"
if [ "$cleaner" == "--clean" ]; then
  cmd "aws --region $REGION s3 rm --recursive $BUCKET/REPO"
fi

step 6 "copy to S3 ############################"
flags="--acl public-read --storage-class STANDARD --recursive"
cmd "aws --region $REGION s3 cp . $BUCKET/REPO $flags"

# Step 6a - Re-upload the offline tarball with content-disposition headers  
# so pgedge-latest-{arch}.tgz downloads with its versioned filename.  
step 6a "recopy offline repo tgz to S3 with headers ############################"
cmd "aws --region $REGION s3 cp $offline_tgz_bndl $BUCKET/REPO/ --acl public-read --content-disposition \"attachment; filename=$offline_tgz_bndl\""

step 7 "Goodbye! ##############################"
exit 0
