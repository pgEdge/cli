# github.com/pgedge/devel/mqtt

Sample usage of Mosquitto MQTT Broker 

## Manifest ##########################

env.sh            : global envionment variable file sourced by each numbered shell script
1-install.sh      : for el9; install and start Mosquitto MQTT Broker on localhost
2-bash-sub.sh     : simple bash script to subscribe to 'nodectl' topic
3a-bash-pub.sh    : simple bash script to publish a message to 'nodectl' topic
3b-python-pub.py  : simple python3 script to publish a message to 'nodectl' topic
4-python-sub.py   : sample python3 daemon to subscribe to 'nodectl' topic and issue a 'nodectl' command
requirements.txt  : the PIP3 needful


