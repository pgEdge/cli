source env.sh

cp ~/.aws/config .

podman build $1 -t $host .

rm -f config
