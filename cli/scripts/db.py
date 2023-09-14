#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, random, json, socket, datetime
import util, fire, meta, subprocess


def pool_add_user(User, Passwd, size, timeout=0):
  """ Coming Soon!"""
  pass


def pool_update_user(User, Passwd=None, size=None, timeout=None):
  """ Coming Soon!"""
  pass


def pool_delete_user(User):
  """ Coming Soon!"""
  pass


def create(db=None, User=None, Passwd=None, Id=None, pg=None):
  """
  Create a pg db with spock installed into it.


   Usage:
       To create a superuser than has access to the whole cluster of db's
          db create -d <db> -U <usr> -P <passwd>

       to create an admin user that owns a specifc tennant database
          db create -I <id>  [-P <passwd>]
      
  """

  if db == None:
    db = os.getenv('pgName', None)

  if User == None:
    User = os.getenv('pgeUser', None)

  ## one way or another, the user that creates the db will have a password
  if Passwd == None:
    Passwd = os.getenv('pgePasswd', None)
    if Passwd == None:
      Passwd = util.get_random_password()

  if pg == None:
    pg_v = util.get_pg_v(pg)
    pg = pg_v[2:]

  nc = "./nodectl "
  ncb = nc + "pgbin " + str(pg) + " "

  privs = ""
  if Id:
    privs = "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN"
    User = "admin_" + str(Id)
    db = "db_" + str(Id)
  elif User and db:
    privs = "SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN"
  else:
    util.exit_message("db_create() must have parms of (-I) or (-U -d)")

  cmd = "CREATE ROLE " + User + " PASSWORD '" + Passwd + "' " + privs
  rc1 = util.echo_cmd(ncb +  '"psql -q -c \\"' + cmd + '\\" postgres"')

  cmd = "createdb '" + db + "' --owner='" + User + "'"
  rc2 = util.echo_cmd(ncb  + '"' + cmd + '"')

  spock_comp = "spock31-pg" + str(pg)
  st8 = util.get_comp_state(spock_comp)
  if st8 in ("Installed", "Enabled"):
    cmd = "CREATE EXTENSION spock"
    rc3 = util.echo_cmd(ncb +  '"psql -q -c \\"' + cmd + '\\" ' + str(db) + '"')
  else:
    rc3 = util.echo_cmd(nc + "install " + spock_comp + " -d " + str(db))

  rcs = rc1 + rc2 + rc3
  if rcs == 0:
    status = "success"
  else:
    status = "error"

  return_json = {}
  return_json["status"] = status
  return_json["db_name"] = db 
  return_json["users"] = []

  user_json={}
  user_json["user"] = User
  user_json["passwd"] = Passwd
  return_json["users"].append(user_json)

  if Id:
    print(util.json_dumps(return_json))

  return


if __name__ == '__main__':
  fire.Fire({
    'create':             create,
    'pool-add-user':      pool_add_user,
    'pool-update-user':   pool_update_user,
    'pool-delete-user':   pool_delete_user,
  })
