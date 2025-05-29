
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time

os.chdir(os.getenv("MY_HOME"))

import fire, util, db

def upgrade_cli(dryrun=False):
    """Upgrade pgEdge CLI to latest stable

       Upgrade pgEdge CLI to latest stable version.

       Example: ./pgedge upgrade-cli --dryrun
       :param dryrun: See what version of the CLI you'd be upgrading too
    """

    util.message(f"upgrade_cli_fire.upgrade_cli({dryrun})", "debug")

    upgrade_script = "upgrade-cli.py"
    url = util.get_value("GLOBAL", "REPO")

    util.message(f"Retrieving {upgrade_script} from {url} ...")
    rc = util.http_get_file(False, upgrade_script, url, util.MY_HOME, False, "")
    if rc is False:
        exit_cleanly(1)

    parms = ""
    if dryrun is True:
        parms = "--dryrun"
    os.system(f"python3 {upgrade_script} {parms}")

    debug_level = int(os.getenv('pgeDebug', '0'))
    if debug_level == 0:
       os.remove(f"{util.MY_HOME}/{upgrade_script}")

    return


if __name__ == "__main__":
    fire.Fire(upgrade_cli)
