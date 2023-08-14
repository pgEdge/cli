
py3V=`python3 --version`
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "Missing Python39+"
  exit 1
fi

rm -f get-pip.py
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py
