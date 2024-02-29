
####################################################################
######          Copyright (c)  2022-2023 PGEDGE             ##########
####################################################################

import argparse, sys, os, tempfile, json, subprocess, getpass
import util, meta

pgver = "pgXX"

MY_HOME = os.getenv("MY_HOME", "")
MY_LOGS = os.getenv("MY_LOGS", "")

pg_home = os.path.join(MY_HOME, pgver)
homedir = os.path.join(MY_HOME, pgver)
logdir = os.path.join(homedir, pgver)

extension_name, default_conf = meta.get_extension_meta("spock32")
print(f"DEBUG: {extension_name}, {default_conf}")
