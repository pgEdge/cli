
set -e
set -x

cd ~
rm -rf venv
/usr/bin/python3 -m venv venv
source ~/venv/bin/activate

pip3 install --upgrade pip
pip3 install --upgrade pip

