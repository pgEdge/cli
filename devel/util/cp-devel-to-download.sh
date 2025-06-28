#!/bin/bash
cd "$(dirname "$0")"

# Validate required sub-directory prefix 
if [ -z "$1" ]; then
  echo "ERROR: Missing required S3 sub-directory prefix for devel repo."
  echo "Usage: $0 <devel_subdir>"
  exit 1
fi
# capture input sub-dir prefix 
devel_input_subdir="$1"

# Source and destination s3 buckets, and the prefix
from_bucket="pgedge-devel"
to_bucket="pgedge-download"
to_backup_bucket="pge-downloads-bo35eb85"
backup_bucket_region="us-east-1"

# Construct final source prefix using the provided sub-directory (s3 prefix)
prefix="REPO/stable/$devel_input_subdir"

# Flags for the s3api copy-object command preserving metadata
flags="--acl public-read --storage-class STANDARD --metadata-directive COPY"

# log file s3 copying for errors
log_file="/tmp/s3-copy-errors-$(date +%Y%m%d-%H%M).log"

echo "Listing objects in s3://$from_bucket/$prefix..."
object_keys=$(aws s3api list-objects --bucket "$from_bucket" --prefix "$prefix" --query "Contents[].Key" --output text)
if [ -z "$object_keys" ] || [ "$object_keys" = "None" ]; then
  error_message="ERROR: No objects found in s3://$from_bucket/$prefix. Check that the sub-directory exists."
  echo "$error_message"
  echo "$error_message" >> "$log_file"
  exit 1
fi

# Batch copying, Set the maximum number of concurrent copy jobs
max_jobs=15
job_count=0

# Copy between buckets in the background &
for key in $object_keys; do

  # strip off everything up to the last slash, then prefix with REPO/
  echo "Copying: s3://$from_bucket/$key -> s3://$to_bucket/REPO/${key##*/}"
  aws s3api copy-object \
    --copy-source "${from_bucket}/${key}" \
    --bucket "$to_bucket" \
    --key "REPO/${key##*/}" \
    $flags > /dev/null 2>>"$log_file" &

  echo "Copying: s3://$from_bucket/$key -> s3://$to_backup_bucket/REPO/${key##*/}"
  aws s3api copy-object \
    --region ${backup_bucket_region} \
    --copy-source "${from_bucket}/${key}" \
    --bucket "$to_backup_bucket" \
    --key "REPO/${key##*/}" \
    $flags > /dev/null 2>>"$log_file" &

  job_count=$((job_count + 1))
  
  # When max_jobs are running, wait for them to finish before launching more
  if (( job_count % max_jobs == 0 )); then
    wait
  fi
done

# Wait for any remaining background jobs to finish
wait
echo "s3 copy operation completed $from_bucket -> $to_bucket and $from_bucket -> $to_backup_bucket"

# Check if the log file is not empty, indicating errors were encountered during copying
if [ -s "$log_file" ]; then
  echo "Warning: Some files may have failed to copy. Please check the log file at: $log_file"
  exit 1
fi

