
set -x

cd ~
pip3 install awscli
mkdir -p ~/.aws
cd ~/.aws
touch config
chmod 600 config
