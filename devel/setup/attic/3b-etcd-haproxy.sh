
set -x

etcdV=3.5.9-1
hapxyV=2.8.0-1

arch=`arch`
url=https://download.postgresql.org/pub/repos/yum/common/pgdg-rhel9-extras/redhat/rhel-9-$arch 

rpm=etcd-$etcdV.rhel9.$arch.rpm
rm -f $rpm
wget $url/$rpm
sudo rpm -ivh $rpm
rm $rpm


rpm=haproxy-$hapxyV.rhel9.$arch.rpm
rm -f $rpm
wget $url/$rpm
sudo rpm -ivh $rpm
rm $rpm



