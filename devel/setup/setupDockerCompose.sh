install="dnf install -y"
url=https://download.docker.com/linux/centos/docker-ce.repo

sudo $install yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo $url/docker-ce.repo

sudo $install docker-ce docker-ce-cli containerd.io
sudo $install docker-compose-plugin
