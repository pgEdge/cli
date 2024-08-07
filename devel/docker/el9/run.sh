
source env.sh

podman stop $host
podman run -d --rm --name $host --hostname $host --security-opt label:disable -p $port:22 $host
sleep 1
ssh-keygen -f ~/.ssh/known_hosts -R "[localhost]:$port"
ssh-copy-id -o StrictHostKeyChecking=accept-new -p $port build@localhost >/dev/null 2>&1
sleep 1
ssh -p $port build@localhost
