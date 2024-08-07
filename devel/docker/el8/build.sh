cp ~/.aws/config .

podman build $1 -t el8 .

rm -f config
