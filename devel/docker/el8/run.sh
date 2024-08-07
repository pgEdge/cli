podman stop -l
podman run -d --rm --hostname el8 -p 3333:22 --security-opt label:disable el8
ssh-keygen -f ~/.ssh/known_hosts -R '[localhost]:3333'
ssh-copy-id -o StrictHostKeyChecking=accept-new -p 3333 build@localhost >/dev/null 2>&1
ssh -p 3333 build@localhost

#-v $IN:/home/build/dev/in:Z \
#	-v $OUT:/home/build/dev/out:Z \
#podman run -d --rm -p 2222:22 -p 8080:80 -v ./html:/var/www/html:Z build-amd
