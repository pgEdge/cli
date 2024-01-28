
set -x

grep el8 /etc/os-release
rc=$?
if [ "$rc" == "0" ]; then
  ./1a-python39.sh
fi

./1b-pip3.sh 
./1c-bashrc.sh 
./1d-awscli.sh

