Run pgEdge in a docker container
==

Test environment of **pgEdge Platform** running in two Docker containers, deployed using `docker-compose`.

Intention of how this should run:
---

How this is _supposed_ to be run:

```
docker-compose build
docker-compose up
```

Once the networking is finished, this will install pgEdge Platform
with a database called `demo`. It will install the `spock` extension, 
create a `foobar` table, and configure replication for that table. 
A successful run will show out of 

```
SELECT * FROM spock.node;
```

with two records, one for each node, showing on both nodes


To reset:
---
``
docker-compose down
docker-compose rm
``

Other notes
===========
You don't have a `systemctl` inside a docker container, but the `nodectl` scripts
assume that it is there.  There's a `fake-systemctl` bash script that gets copied
into the container to try and mimic this functionality.

The ENTRYPOINT of the docker container is set to `forever.sh`, so that by
pressing CTL-D you don't accidentally stop the container. It also means that
when you run in `docker-compose`, once the initialization is all done, it will
pause (for a day) for testing.

