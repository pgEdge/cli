podman stop -l
podman run -d --rm --hostname build-amd -p 2222:22 \
	--security-opt label:disable \
	build-amd
ssh-keygen -f ~/.ssh/known_hosts -R '[localhost]:2222'
ssh-copy-id -o StrictHostKeyChecking=accept-new -p 2222 build@localhost >/dev/null 2>&1
ssh -p 2222 build@localhost

#-v $IN:/home/build/dev/in:Z \
#	-v $OUT:/home/build/dev/out:Z \
#podman run -d --rm -p 2222:22 -p 8080:80 -v ./html:/var/www/html:Z build-amd
