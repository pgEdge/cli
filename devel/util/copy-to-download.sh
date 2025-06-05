#!/bin/bash
cd "$(dirname "$0")"

source $PGE/env.sh

export BUCKET=s3://pgedge-download
export BACKUP_BUCKET=s3://pge-downloads-bo35eb85
export BACKUP_REGION=us-east-1

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

sleep 2
cd $outDir
ls
sleep 2

flags="--acl public-read --storage-class STANDARD --recursive"

buckets=(
  "$REGION:$BUCKET/REPO"
  "$BACKUP_REGION:$BACKUP_BUCKET/REPO"
)

set -x
rc=0

for entry in "${buckets[@]}"; do
  IFS=':' read -r region bucket <<< "$entry"
  aws --region "$region" s3 cp . "$bucket" $flags
  rc=$?
  if [ "$rc" -ne 0 ]; then
    exit $rc
  fi
  sleep 2
done

# Additional check for offline bundle, if exists then re-upload with
# content disposition header
if [ $rc -eq 0 ] && [ -f "$offline_tgz_bndl" ]; then
    echo "Uploading offline bundle with content-disposition header"
    for entry in "${buckets[@]}"; do
      IFS=':' read -r region bucket <<< "$entry"
      aws --region $region s3 cp "$offline_tgz_bndl" "$bucket" \
          --acl public-read \
          --content-disposition "attachment; filename=$offline_tgz_bndl"
      rc=$?  # Capture exit code from second upload
      if [ "$rc" -ne 0 ]; then
        exit $rc
      fi
      sleep 2
    done
fi

exit $rc
