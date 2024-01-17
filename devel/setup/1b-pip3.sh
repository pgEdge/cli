
py3V=`python3 --version`
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "Missing Python3.9"
  exit 1
fi

url=https://bootstrap.pypa.io/get-pip.py

rm -f get-pip.py
curl -o get-pip.py $url
python3 get-pip.py
rm get-pip.py
