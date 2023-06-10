
source 0-env.sh

$snap install mosquitto

$certbot certonly --standalone --standalone-supported-challenges http-01 -d test1.pgedge.org
