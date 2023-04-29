set -x 

if [ "$BLD" == "" ] || [ "$IN" == "" ]; then
  echo ERROR: Invalid Environment
  exit 1
fi

cd $BLD
rc=$?
if [ "$rc" != "0" ]; then
  exit 1
fi
cp -p $NC/devel/pgbin/build/*.sh .

cd $IN
cp $NC/devel/util/in/pull-s3.sh .
./pull-s3.sh
chmod 755 *.sh
