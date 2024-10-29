
set -x

sudo docker run --name supv -v my-pgdata:/opt/pgedge/data -d supv
