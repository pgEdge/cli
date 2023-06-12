
yum="sudo dnf -y"

$yum install epel-release

sudo /usr/bin/crb enable
$yum makecache

$yum install snapd

sudo systemctl enable --now snapd.socket

