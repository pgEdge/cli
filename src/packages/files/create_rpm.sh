#!/bin/sh


/build/oscg_pgrpm_pgcentral.sh --major_version 9.6 \
                               --minor_version 0 --release 1 \
                               --rpm_release 1 --pkg_name postgres \
                               --init_script /build/startup/sys-v/init-template  \
                               --source_dir /build/output/el7/20161004/1475611351
