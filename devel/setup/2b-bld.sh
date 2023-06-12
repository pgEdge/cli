set -x 

if [ "$BLD" == "" ]; then
  echo ERROR: Invalid Environment
  exit 1
fi

cd $BLD
rc=$?
if [ "$rc" != "0" ]; then
  exit 1
fi
cp -p $NC/devel/pgbin/build/*.sh .

