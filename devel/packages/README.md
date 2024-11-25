These are the scripts that will be run for using FPM to build our
RPM & DEB packages

[FPM](https://fpm.readthedocs.io/en/latest/installation.html)

# know limtaions: 
- only tested on el9
- should work on all el8 & el9 & (even) fd40/el10
- gotta tweak a couple things before it will run on debian/ubuntu


# manual steps he needful manually:

- use `wget` to download a `tgz` bundle to /tmp/pgedge

- look for these scripts in the `data/conf/cache/packages` directory

- run  `sudo before-install.sh` script to create the `pgedge` user

- copy the tgz bundle to `/opt/pgedge`
```
  cd /opt
  sudo mkdir pgedge
  sudo cp -r /tmp/pgedge/* pgedge/.
```

- run `sudo after-install.sh` (and do what it says)
