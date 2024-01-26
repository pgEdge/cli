sudo yum install -y bind bind-utils
sudo systemctl enable named
sudo systemctl start named
sudo yum install -y avahi

