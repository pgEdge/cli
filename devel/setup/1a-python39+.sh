
echo " "
echo "# run 1a-python39+"
py3V=`python3 --version`
py3M=`echo $py3V | awk '{print $2}' | sed -r 's/([^.]+.[^.]*).*/\1/'`

echo "# py3V = $py3V"
echo "# py3M = $py3M"

set -x

um=yum
apt --version
rc=$?
if [ $rc == "0" ]; then
  um=apt
fi

if [ "$py3M" == "3.6" ]; then
   if [ "$um" == "yum" ]; then
     sudo yum install -y python39 python39-devel python39-pip gcc
   else
     echo "Platform not supported"
     exit 1
   fi
else
   if [ "$um" == "yum" ]; then
     sudo yum install -y python3-devel python3-pip gcc
   else
     sudo apt install -y python3-dev python3-pip python3-venv gcc
   fi
fi


cd ~
python3 -m venv venv
source ~/venv/bin/activate

pip3 install --upgrade pip
