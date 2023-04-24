Initial prototype to run pgEdge in a docker container
==

Working to try and get a test environment of pgEdge running in two Docker containers, controlled by docker-compose.

Intention of how this should run:
---

How this is _supposed_ to be run:

```
docker-compose up
```


To reset:
---
``./run2 redo``

* Does a docker-compose down and then removes the Docker image


To build:
---
``./run2``

* recreates the docker image test/pgedge



Other notes
===========
You don't have a systemctl inside a docker container, but the nodectl scripts
assume that it is there.  There's a 'fake-systemctl' bash script that gets copied
into the container to try and mimic this functionality.

The ENTRYPOINT of the docker container is set to 'forever.sh', so that by
pressing CTL-D you don't accidentally stop the container. It also means that
when you run in docker-compose, once the initialization is all done, it will
pause (for a day) for testing.

Different flavours of Linux:
============================
* Dockerfile.debian
* Dockerfile.rockylinux


