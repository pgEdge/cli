#!/usr/bin/env python3

#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os
import json
import util
import fire
import time
import warnings

def start(verbose=False):
    util.run_rcommand(
        f"sudo systemctl daemon-reload", 
        message="", verbose=verbose
    )
    util.run_rcommand(
        f"sudo systemctl start patroni",
        message="", verbose=verbose
    )

def stop(verbose=False):
    util.run_rcommand(
        f"sudo systemctl daemon-reload", 
        message="", verbose=verbose
    )
    util.run_rcommand(
        f"sudo systemctl stop patroni",
        message="", verbose=verbose
    )

def status(verbose=False):
    util.run_rcommand(
        f"sudo systemctl daemon-reload", 
        message="", verbose=verbose
    )
    util.run_rcommand(
        f"sudo systemctl status patroni",
        message="", verbose=verbose
    )

if __name__ == "__main__":
    fire.Fire({
        "start": start,
        "stop": stop,
        "status": status,
    })

