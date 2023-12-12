
if [ "$IN" == "" ]; then
  echo "ERROR: Missing \$IN environment variable"
  exit 1
fi

mkdir -p $IN
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: Couldn't make $IN directory"
  exit 1
fi

pull=$NC/devel/util/in/pull-s3.sh
if [ "$NC" == "" ] || [ ! -f "$pull" ]; then
  echo "ERROR: missing pull file \"$pull\""
  exit 1
fi

cd $IN
cp $NC/devel/util/in/pull-s3.sh .
./pull-s3.sh
chmod 755 *.sh


cp $IN/ctlibs/*.bz2  $OUT/.


