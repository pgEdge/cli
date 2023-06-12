
set -x

rm -f get-pip.py
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py
