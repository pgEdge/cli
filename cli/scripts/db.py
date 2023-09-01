#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess, requests


def pool_add_user(User, Passwd, size, timeout=0):
  """ Coming Soon!"""
  pass


def pool_update_user(User, Passwd=None, size=None, timeout=None):
  """ Coming Soon!"""
  pass


def pool_delete_user(User):
  """ Coming Soon!"""
  pass


if __name__ == '__main__':
  fire.Fire({
    'pool-add-user':      pool_add_user,
    'pool-update-user':   pool_update_user,
    'pool-delete-user':   pool_delete_user,
  })
