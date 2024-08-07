cp ~/.aws/config .

podman build $1 -t build-amd .

rm -f config
