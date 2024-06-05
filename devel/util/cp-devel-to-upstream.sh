#!/bin/bash
cd "$(dirname "$0")"

from_bucket=s3://pgedge-devel/REPO
to_bucket=s3://pgedge-upstream/REPO

flags="--acl public-read --storage-class STANDARD --recursive"

cmd="aws s3 cp $from_bucket $to_bucket $flags"
echo $cmd

sleep 3

$cmd
rc=$?
echo "rc=($rc)"
exit $rc

