#!/bin/bash
cd "$(dirname "$0")"

# Enhanced build script with support for 'stable' and 'current' build modes.
# - 'stable' mode: Builds packages with all stable components + the latest CLI + offline bundle
#                  suitable for reliable, production-ready releases.
#                  Stable builds are pushed to pgedge-devel repo into the REPO/stable/<build-suffix>
#
# - 'current' mode: Extends 'stable' mode by including the latest (in-development/unstable) spock 
#         (e.g. spock50) which will be extended in future to contain more of the in dev/unstable components
#         Current builds are pushed to pgedge-devel repo into the REPO/current/<build-suffix>
#
# This script is now the primary build tool, replacing the older build_to_devel.sh,
# and is called by corresponding workflows in pgedge/cli for stable (amd8 and arm9) and current (amd8 and arm9)
# builds. It supports both automated daily runs and manual triggers with customizable options via switches.
# 
# New switches introduced:
# - -m MODE: Specifies the build mode ('stable' or 'current', defaults to 'stable').
# - -c COMPONENT: Required for 'current' mode, specifies the Spock component (e.g., spock50).
# - -b BRANCH: For 'current' mode, sets the branch for the Spock component (defaults to 'main').
# - -p PGVERS: For 'current' mode, comma-separated PG versions to build (defaults to '15,16,17').
# - -d S3SUBDIR: Sets the S3 subdirectory for uploads (defaults to MMDD, e.g., 0612).
# - -x: Enables cleaning the S3 subdirectory before upload.
# 
# The script handles S3 uploads, lifecycle policies, and build artifacts, adapting behavior
# based on the selected mode. 
# 
#
# Note :  'stable' mode relies solely on -d and -x 
# while  additional inputs -c, -b  -p are associated with 'current' mode only 

#Argument parsing using getopts for stable/current modes and options
MODE="stable"
COMPONENTNAME=""
BRANCH="main"
PGVERS="15,16,17"
subdir=$(date +%m%d)
cleaner=""

show_help() {
  cat << EOF
Usage: $0 [OPTIONS]
  -m MODE         Build mode: 'stable' (default) or 'current' (includes in-dev spock)
  -c COMPONENT    Spock component to build (required in current mode, e.g. spock50)
  -b BRANCH       Branch to use for spock component (default: main, current mode only)
  -p PGVERS       Comma-separated PG versions (default: 15,16,17, current mode only)
  -d S3SUBDIR     S3 subdirectory (default: MMDD)
  -x              Clean S3 subdir before upload, optional
  -h              Show help

Examples:
  $0 -d 0522 -x
  $0 -m stable -d 0522
  $0 -m current -c spock50 -b main -p 15,16,17 -d 0522
EOF
}

while getopts "m:c:b:p:d:xh" opt; do
  case $opt in
    m) MODE="$OPTARG" ;;
    c) COMPONENTNAME="$OPTARG" ;;
    b) BRANCH="$OPTARG" ;;
    p) PGVERS="$OPTARG" ;;
    d) subdir="$OPTARG" ;;
    x) cleaner="--clean" ;;
    h) show_help; exit 0 ;;
    \?) show_help; exit 1 ;;
  esac
done

if [[ "$MODE" == "current" && -z "$COMPONENTNAME" ]]; then
  echo "[ERROR] -c COMPONENT is required in current mode"
  show_help
  exit 1
fi

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
step -2 "Pre-checks: Environment, Disk Space & S3 Access"

check_env_vars
check_disk_space
check_s3_access

# Step -1: If mode is current, set the s3 prefix and execute get-and-build-spock.sh that fetches latest source from spock
#           branch and builds its binaries using the pgbin-build project.
#           Else, in stable mode, only set the s3 prefix.
if [[ "$MODE" == "current" ]]; then
  step -1 "set current S3 prefix, run get-and-build-spock.sh to build latest spock #####################"
  prefix="REPO/current/$subdir"
  if ! "$BLD/get-and-build-spock.sh" -b "$BRANCH" -c "$COMPONENTNAME" -p "$PGVERS"; then
    echo "[ERROR] get-and-build-spock.sh failed!"
    exit 1
  fi
else
  step -1 "set stable S3 prefix #########################"
  prefix="REPO/stable/$subdir"
fi
echo "# Using S3 prefix: $prefix"

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
# call make_tgz.sh which also now takes the mode (stable/current)
./make_tgz.sh -m "$MODE"
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

# Compute the base prefix (e.g., REPO/stable/ or REPO/current/)
base_prefix="${prefix%/*}/"

# Define a lifecycle policy JSON dynamically for all objects under the base prefix
step 6b "Set lifecycle policy for objects under $base_prefix to auto expire/delete after 7 days"
policy='{
  "Rules": [
    {
      "ID": "ExpireBuilds_'"$MODE"'",
      "Filter": { "Prefix": "'"$base_prefix"'" },
      "Status": "Enabled",
      "Expiration": { "Days": 7 }
    }
  ]
}'
cmd "aws --region $REGION s3api put-bucket-lifecycle-configuration --bucket $BUCKET_NAME --lifecycle-configuration '$policy'"

step 7 "Goodbye! ##############################"
echo "Script completed successfully"

exit 0
