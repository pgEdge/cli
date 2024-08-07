cp ~/.aws/config .

sudo docker build $1 -t pgedge/build-el8   ./

rm config
