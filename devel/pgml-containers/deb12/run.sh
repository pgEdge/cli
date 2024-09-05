podman run -ti -p 127.0.0.1:65432:5432 -v deb12-home:/home/mledge --rm --device=nvidia.com/gpu=0 -d deb12 
