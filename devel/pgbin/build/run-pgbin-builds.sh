
if [ `uname` == "Linux" ]; then
  sudo yum -y update
fi

./sharedLibs.sh

./build-all-pgbin.sh 14 -c
./build-all-pgbin.sh 15 -c

