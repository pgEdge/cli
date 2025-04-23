#!/bin/bash
cd "$(dirname "$0")"

source $PGE/env.sh

# Show progress updates if stdout is a terminal;
# if not (e.g. redirected to a log file), disable them to avoid s3 copy progress noise
if [ -t 1 ]; then
  PROGRESS_FLAG=""
else
  PROGRESS_FLAG="--no-progress"
fi

# Global variable to track the current step.
CURRENT_STEP="Initialization"

# Set a trap to catch any errors and report the current step.
trap 'echo "ERROR: Failure during step: $CURRENT_STEP"; exit 1' ERR

# --- S3 Bucket and Name Declarations ---
# Set the S3 bucket (change this as needed)
export BUCKET="s3://pgedge-devel"

# offline tgz bundle name
offline_tgz_bndl="pgedge-$hubVV-$OS.tgz"

# Export the bucket name (remove s3://) only as some s3 commands require bucket name only
export BUCKET_NAME=$(echo $BUCKET | sed 's#s3://##')

# Functions

cmd () {
  echo "# $1"
  eval "$1"
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: rc=$rc  Stopping Script"
    exit $rc
  fi
}

step () {
  CURRENT_STEP="$1 - $2"
  local ts
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo ""
  echo "[$ts] ## step $CURRENT_STEP"
}

# Check required environment variables.
check_env_vars() {
  if [ -z "$PGE" ] || [ -z "$OUT" ] || [ -z "$HIST" ]; then
    echo "ERROR: One or more required environment variables are not set."
    echo "PGE: '$PGE', OUT: '$OUT', HIST: '$HIST'"
    exit 1
  fi
}

# Ensure around 5GB free space is available on the filesystem containing $OUT.
check_disk_space() {
  # Required is approx 2.5GB, keeping a check around 5GB to account for interim files.
  REQUIRED_DISK=5000000
  available=$(df -P "$OUT" | awk 'NR==2 {print $4}')
  echo "Disk space available on $OUT: ${available} KB (Required: ${REQUIRED_DISK} KB)"
  if [ "$available" -lt "$REQUIRED_DISK" ]; then
    echo "ERROR: Not enough disk space to build platform packages. Approx 5GB required"
    exit 1
  fi
}

# Check that the S3 bucket is accessible.
check_s3_access() {
  if ! aws --region $REGION s3api head-bucket --bucket "$BUCKET_NAME" > /dev/null 2>&1; then
    echo "ERROR: S3 bucket $BUCKET_NAME does not exist or is not accessible."
    exit 1
  fi
}

# --- Pre-checks (Step -1) ---
step -1 "Pre-checks: Environment, Disk Space & S3 Access"

check_env_vars
check_disk_space
check_s3_access

# -------------------------------
# New Argument Parsing for Subdirectory and Clean Flag
# Usage: ./build_to_devel.sh [subdirectory] [--clean]
# If no custom subdirectory is provided then MMDD is used and --clean is not set.
subdir=$(date +%m%d)
cleaner=""

# Parse input arguments
if [ "$1" == "--clean" ]; then
  cleaner="--clean"
  shift
fi

if [ -n "$1" ]; then
  subdir="$1"
  if [ "$2" == "--clean" ]; then
    cleaner="--clean"
  fi
fi

echo "# Using subdirectory: $subdir"
if [ "$cleaner" == "--clean" ]; then
  echo "# Clean flag is set"
fi

# Calculate S3 path prefix (REPO/stable/<subdir>)
prefix="REPO/stable/$subdir"
echo "# Using S3 prefix: $prefix"
# -------------------------------

step 0 "## initialization  #######################"
echo "#  BUCKET = $BUCKET"

now=`date '+%F %r %Z'`
echo "#     now = $now"

run_day=`date +%j`
echo "# run_day = $run_day"

vers="15 16 17"
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
echo "Building tgz bundle : $offline_tgz_bndl"
./make_tgz.sh
sleep 9
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
  cmd "aws --region $REGION s3 rm --recursive $BUCKET/$prefix"
fi

# s3 copy
step 6 "copy to S3 ############################"
flags="--acl public-read --storage-class STANDARD --recursive"
cmd "aws --region $REGION s3 cp . $BUCKET/$prefix $flags $PROGRESS_FLAG"

# Step 6a - Re-upload the offline tarball with content-disposition headers
# so pgedge-latest-{arch}.tgz downloads with its versioned filename.
step 6a "recopy offline repo tgz to S3 with headers ############################"
cmd "aws --region $REGION s3 cp $offline_tgz_bndl $BUCKET/$prefix/ --acl public-read --content-disposition \"attachment; filename=$offline_tgz_bndl\" $PROGRESS_FLAG"

# Define a lifecycle policy JSON for all objects under the REPO/stable to auto expire after 7 days
step 6b "Set lifecycle policy for the objects under REPO/stable to auto expire/delete after 7 days"
policy='{
  "Rules": [
    {
      "ID": "ExpireStableBuilds",
      "Filter": { "Prefix": "REPO/stable/" },
      "Status": "Enabled",
      "Expiration": { "Days": 7 }
    }
  ]
}'
cmd "aws --region $REGION s3api put-bucket-lifecycle-configuration --bucket $BUCKET_NAME --lifecycle-configuration '$policy'"

step 7 "Goodbye! ##############################"
echo "Script completed successfully"
exit 0


