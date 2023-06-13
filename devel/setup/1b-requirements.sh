
set -x

sudo dnf install -y python3-psutil

pip3 install --user -r $NC/requirements.txt

