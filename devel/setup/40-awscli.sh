
cd ~

flags="--upgrade --no-warn-script-location"
pip3 install $flags awscli
mkdir -p ~/.aws
cd ~/.aws
touch config
chmod 600 config

echo " "
echo "Now go put your AWS credentials in ~/.aws/config file"
