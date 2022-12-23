outD=out-20220209

rm -rf history/$outD
mkdir history/$outD

cp -p $OUT/* history/$outD/.

./copy-to-s3.sh $outD
