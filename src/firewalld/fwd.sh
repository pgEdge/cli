sudo dnf -y install firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo systemctl status firewalld

sudo firewall-cmd --reload
