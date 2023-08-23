#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess, requests


def add_user(User, Passwd, size, timeout=0):
  pass


def update_user(User, Passwd=None, size=None, timeout=None):
  pass


def delete_user(User):
  pass


if __name__ == '__main__':
  fire.Fire({
    'add-user':      add_user,
    'update-user':   update_user,
    'delete-user':   delete_user,
  })
