
set -x 

if [ "$IN" == "" ]; then
  echo ERROR: Invalid Environment
  exit 1
fi

mkdir -p $IN

cd $IN
cp $NC/devel/util/in/pull-s3.sh .
./pull-s3.sh
chmod 755 *.sh


