#!/bin/bash
cd "$(dirname "$0")"

source $PGE/env.sh

export BUCKET=s3://pgedge-devel

# Offline bundle name
offline_tgz_bndl="pgedge-$hubVV-$OS.tgz"

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

# Check if $2 is empty
if [[ -z "$2" ]]; then
  echo "Error: Second argument (mode) is required and must be either 'stable' or 'current'."
  exit 1
fi

# Validate allowed values
if [[ "$2" != "stable" && "$2" != "current" ]]; then
  echo "Error: Second argument must be either 'stable' or 'current'."
  exit 1
fi

MODE=$2

sleep 2
cd $outDir
ls
sleep 2

flags="--acl public-read --storage-class STANDARD --recursive"
BR=$BUCKET/REPO/$MODE
set -x

aws --region $REGION s3 cp . $BR $flags
rc=$?
sleep 2

# Additional check for offline bundle, if exists then re-upload with
# content disposition header
if [ $rc -eq 0 ] && [ -f "$offline_tgz_bndl" ]; then
    echo "Uploading offline bundle with content-disposition header"
    aws --region $REGION s3 cp "$offline_tgz_bndl" "$BUCKET/REPO/$MODE" \
        --acl public-read \
        --content-disposition "attachment; filename=$offline_tgz_bndl"
    rc=$?  # Capture exit code from second upload
fi

exit $rc
