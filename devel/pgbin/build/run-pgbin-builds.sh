
#if [ `uname` == "Linux" ]; then
#  sudo yum -y update
#fi
#
#./sharedLibs.sh

./build-all-pgbin.sh 11 -c
./build-all-pgbin.sh 12 -c
./build-all-pgbin.sh 13 -c
./build-all-pgbin.sh 14 -c
./build-all-pgbin.sh 15 -c
#./build-all-pgbin.sh 16 -c

