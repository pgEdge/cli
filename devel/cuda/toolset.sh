set -x

tk_v=12.5.1
url=https://developer.download.nvidia.com/compute/cuda

rpm_f=cuda-repo-rhel8-12-5-local-${tk_v}_555.42.06-1.x86_64.rpm

rm -f $rpm_f
wget $url/$tk_v/local_installers/$rpm_f
sudo rpm -i $rpm_f 
sudo dnf clean all
sudo dnf -y install cuda-toolkit-12-5
