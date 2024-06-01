
echo " "
echo "# run 1a-python39+"
py3V=`python3 --version`
py3M=`echo $py3V | awk '{print $2}' | sed -r 's/([^.]+.[^.]*).*/\1/'`

echo "# py3V = $py3V"
echo "# py3M = $py3M"

set -x

if [ "$py3M" == "3.6" ]; then
   sudo yum install -y python39 python39-devel
fi

sudo yum install python3-devel gcc

cd ~
python3 -m venv venv
source ~/venv/bin/activate

pip3 install --upgrade pip
