
set -x

export BUCKET=s3://pgedge-upstream
./copy-to-s3.sh $1
rc=$?
if [ ! "$rc" == "0" ]; then
  exit $rc
fi

export BUCKET=s3://pgedge-download
./copy-to-s3.sh $1
rc=$?
exit $rc

