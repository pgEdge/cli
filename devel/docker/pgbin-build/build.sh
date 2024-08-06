cp ~/.aws/config .

podman build $1 -t pgedge/build-el8   ./

rm config
