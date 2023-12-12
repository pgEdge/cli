
py3V=`python3 --version`
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "Missing Python3+"
  exit 1
fi

url=https://bootstrap.pypa.io/get-pip.py
if [ "$py3V" == "Python 3.6.8" ]; then
  url=https://bootstrap.pypa.io/pip/3.6/get-pip.py
fi

rm -f get-pip.py
curl -o get-pip.py $url
python3 get-pip.py
rm get-pip.py
