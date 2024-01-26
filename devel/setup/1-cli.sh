
set -x

grep /etc/os-release el8
rc=$?
if [ "$rc" == "0" ]; then
  ./1a-python39.sh
fi

./1b-pip3.sh 
./1c-bashrc.sh 
./1d-awscli.sh

