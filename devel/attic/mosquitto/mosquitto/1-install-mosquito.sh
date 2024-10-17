
set -x

sudo add-apt-repository ppa:mosquitto-dev/mosquitto-ppa -y
sudo apt install mosquitto mosquitto-clients -y

conf=/etc/mosquitto/mosquitto.conf

grep allow_anonymous $conf
rc=$?
if [ ! "$rc" == "0" ]; then
  sudo sh -c "cat mosquitto.conf >> $conf"
fi

sudo systemctl restart mosquitto
sudo systemctl status mosquitto

exit 0



sudo yum -y install mosquitto

sudo systemctl enable mosquitto

sudo systemctl start mosquitto
