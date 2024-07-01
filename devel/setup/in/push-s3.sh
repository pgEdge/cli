
cmd="aws --region $REGION s3 sync . $BUCKET/IN $1 $2"
echo $cmd
sleep 3

$cmd
rc=$?

echo "rc($rc)"
exit $rc

