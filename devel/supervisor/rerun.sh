
set -x

sudo docker rm -f supv

sudo docker volume rm -f my-pgdata
sudo docker volume create my-pgdata

./run.sh

