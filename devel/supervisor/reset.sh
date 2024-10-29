
set -x

sudo docker rm -f supv

sudo docker volume rm -f my-pgdata
sudo docker volume create my-pgdata

sudo docker run --name supv -v my-pgdata:/opt/pgedge/data -d supv

