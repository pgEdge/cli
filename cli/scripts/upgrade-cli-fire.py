
#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys, time

os.chdir(os.getenv("MY_HOME"))

import fire, util, db

def upgrade_cli(dryrun=False, force=False):
    """Upgrade pgEdge CLI to latest stable

       Upgrade pgEdge CLI to latest stable version

       Example: ./pgedge upgrade-cli --dryrun
       :param dryrun: See what version of the CLI you'd be upgrading too
       :param force: Don't ask before upgrading CLI (always False when doing a --dryrun)
    """

    util.message(f"upgrade_cli_fire.upgrade_cli({dryrun}, {force})", "debug")

    print("STUB:  Hello from upgrade-cli-fire.py")

    return

if __name__ == "__main__":
    fire.Fire(upgrade_cli)
