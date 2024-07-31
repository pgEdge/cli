
# Copyright (C) 2023-2024 Denis L. Lussier #

import os, sys

VERSION = 0.1

VALID_OS = [ "el8", "el9", "el10", "ubu22", "ubu24", "deb11", "deb12" ]


def is_apt():
  rc = os.system("apt --version > /dev/null 2>&1")
  if rc == 0:
     return True

  return False


def is_yum():
  rc = os.system("yum --version > /dev/null 2>&1")
  if rc == 0:
     return True

  return False


def get_os():
    return("???")


