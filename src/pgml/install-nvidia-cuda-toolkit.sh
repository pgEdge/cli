set -x

TK_V=12.5.1
URL=https://developer.download.nvidia.com/compute/cuda

install_rpm () {
  rpm_f=cuda-repo-rhel8-12-5-local-${TK_V}_555.42.06-1.x86_64.rpm

  rm -f $rpm_f
  wget $URL/$TK_V/local_installers/$rpm_f
  sudo rpm -i $rpm_f 
  sudo dnf clean all
  sudo dnf -y install cuda-toolkit-12-5
  rm $rpm_f
}

install_deb () {
  pfx=cuda-repo-debian12-12-5-local
  deb_f=${pfx}_$TK_V-555.42.06-1_amd64.deb
  install="sudo apt-get -y install"

  rm -f $deb_f
  wget $URL/$TK_V/local_installers/$deb_f
  sudo dpkg -i $deb_f
  sudo cp /var/$pfx/cuda-*-keyring.gpg /usr/share/keyrings/
  $install software-properties-common
  sudo add-apt-repository -y contrib
  sudo apt-get -y update
  $install glx-alternative-nvidia
  $install cuda-toolkit-12-5 nvidia-smi
  rm $deb_f
}

apt --version
rc=$?
if [ "$rc" == "0" ]; then
  install_deb
else
  install_rpm
fi
