#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import os, sys, re, json, datetime, logging
import util, meta, api

from urllib import request as urllib2

PGDG_REPO_LIST="json-pgdg-repo-list"

YUM_LIST = ['el8', 'el9']
APT_LIST = ['trusty', 'xenial', 'bionic']

my_logger = logging.getLogger('cli_logger')


def discover(p_ver, p_isSILENT=False, p_isJSON=False, p_isYES=False):
  if not p_isJSON:
    print("\nDiscover pgdg v" + str(p_ver))
  [pghome, pgver, svcname, svcfile, datadir, port, logdir] = get_pgdg_base(p_ver, p_isJSON)

  if pghome in ["1", "2", "3"]:
    if not p_isJSON:
      print("  not found")
    return(int(pghome))
  else:
    if not p_isJSON:
      print("   pghome = " + pghome)
      print("    pgver = " + pgver)
      print("  svcname = " + svcname)
      print("  svcfile = " + svcfile)
      print("  datadir = " + datadir)
      if port != "1":
        print("     port = " + port)
      print("   logdir = " + logdir)

    repo = "pgdg" + p_ver.replace(".","")
    if not p_isYES and not p_isJSON:
      try:
        p_install = raw_input("Do you want to install CLI for existing {0} instance:(y/n)".format(repo))
        if p_install in ("y", "Y"):
          p_isYES=True
      except Exception as e:
        p_isYES = False
    if p_isYES:
      meta.put_components(repo, "pgdg", pgver + "-1", "amd", port, "Enabled",
                          "on", datadir, logdir, svcname, "postgres")
      return (0)

  return(4)


def get_pgdg_base(p_ver, p_isJSON):
  basedir = None
  ver = p_ver
  svcname = None
  datadir = None
  port = None
  logdir = None
  to_devnull = " >/dev/null 2>&1"

  ####### (1) PGHOME ##############################
  if util.get_os() in YUM_LIST:  
    basedir = "/usr/pgsql-" + ver
  else:
    basedir = "/usr/lib/postgresql/" + ver

  pgbin = basedir + "/bin/postgres"
  if not os.path.isfile(pgbin):
    print("  PGHOME could not be located at " + pgbin)
    return ("1111111")

  ###### (2) Service Control File #################
  if util.get_os() in APT_LIST:
    svcname = "postgresql"
  else:
    svcname = "postgresql-" + ver

  if util.is_systemd():
    sysdir = util.get_systemd_dir()
    svcfile = sysdir + "/" + svcname + ".service"
  else:
    sysdir = "/etc/init.d"
    svcfile = sysdir + "/" + svcname

  if not os.path.isfile(svcfile):
    print("ERROR: ServiceFile not found (" + svcfile + ")")
    return ("2222222")

  ###### (3) DATADIR ###############################
  if util.get_os() in YUM_LIST:
    datadir = "/var/lib/pgsql/" + ver + "/data"
  else:
    datadir = "/var/lib/postgresql/" + ver + "/main"

  cmd = "sudo ls " + datadir
  rc = os.system(cmd + to_devnull)
  if rc != 0:
    print("ERROR: DataDir not found (" + datadir + ")")
    return ("3333333")

  ##### LOOK FOR PORT ####################
  pidfile = datadir + "/postmaster.pid"
  cmd = "sudo ls " + pidfile
  rc = os.system(cmd + to_devnull)
  if rc == 0:
    cmd = "sudo cat " + pidfile + " | sed -n '4p'"
    port = util.getoutput(cmd)
  else:
    port = "1"

  ##### LOOK FOR LOGDIR ##################
  if util.get_os() in APT_LIST:
    logdir = "/var/log/postgresql"
  else:
    logdir = datadir + "/pg_log"
  cmd = "sudo ls " + logdir
  rc = os.system(cmd + to_devnull)
  if rc != 0:
    logdir = ""
  
  return([basedir, ver, svcname, svcfile, datadir, port, logdir])


## retrieve json file from REPO
def get_json_file(p_file, p_isJSON):
  json_file = p_file + ".txt"
  repo = util.get_value("GLOBAL", "REPO")
  repo_file = repo + "/" + json_file
  out_dir = os.getenv("MY_HOME") + os.sep + "conf" + os.sep + "cache"

  if util.http_get_file(False, json_file, repo, out_dir, False, ""):
    out_file = out_dir + os.sep + json_file
    try:
      return(json.loads(util.read_file_string(out_file)))
    except:
      pass

  util.exit_message("Cannot process json_file '" + p_file + "'", 1, p_isJSON)


## check whether a postgresql repo (yum or apt) is installed
def is_installed(p_repo):
  this_os = util.get_os()
  if this_os in YUM_LIST:
    cmd = "sudo yum repolist | grep " + p_repo + " >/dev/null"
    rc = os.system(cmd)
    if rc == 0:
      return(True)

  if this_os in APT_LIST:
    repo_file_name = get_apt_repo_file_name()
    if os.path.isfile(repo_file_name):
      return(True)

  return(False)


def get_apt_repo_file_name():
    rf_prefix = "/var/lib/apt/lists/apt.postgresql.org_pub_repos_apt_dists_"
    rf_suffix = "_main_binary-amd64_Packages"
    return(rf_prefix + util.get_os() + "-pgdg" + rf_suffix)


## list repositories
def list(p_isJSON):
  repo_dict = get_json_file(PGDG_REPO_LIST, p_isJSON)
  os = util.get_os()
  kount = 0
  lList = []
  for rl in repo_dict:
    lDict = {}
    if os == rl['os']:
      kount = kount + 1
      lDict['repo'] = rl['repo']
      if is_installed(rl['repo']):
        lDict['status'] = "Installed"
      else:
        lDict['status'] = ""
      lList.append(lDict)

  if kount == 0:
    msg = "No repo's available for os = " + os
    util.exit_message(msg, 1, p_isJSON)

  keys = ['repo', 'status']
  headers = ['Repo', 'Status']

  if p_isJSON:
    print(json.dumps(lList, sort_keys=True, indent=2))
  else:
    print(api.format_data_to_table(lList, keys, headers))

  return 0


def get_repo(p_repo, p_isJSON):
  if util.get_os() in APT_LIST:
    jf = "json-" + p_repo
    pkg_mgr = "apt"
  else:
    jf = "json-" + p_repo + "-" + util.get_os()
    pkg_mgr = "yum"
  rd = get_json_file(jf, p_isJSON)

  pkg_prod = get_json_file("json-pgdg-pkg-prod", p_isJSON)
  pkg_filter = []
  for p in pkg_prod:
    try:
      p[pkg_mgr]
      pkg_filter.append(p[pkg_mgr].replace('XX', rd['ver']))
    except:
      pass

  key = ""
  if util.get_os() in APT_LIST:
    key = rd['key']
  
  return([rd['repo-type'], rd['name'], rd['url'], rd['package'], key, pkg_filter])


def is_repo(p_repo, p_isJSON):
  repo_dict = get_json_file(PGDG_REPO_LIST, p_isJSON)
  os = util.get_os()
  for rl in repo_dict:
    if os == rl['os']:
      if rl['repo'] == p_repo:
        return(True)
  return(False)


def validate_os(p_isJSON):
  os = util.get_os()
  if (os in YUM_LIST) or (os in APT_LIST):
    return;
  util.exit_message("OS '" + os + "' not supported for this command.", 1, p_isJSON)


def install_packages(p_repo, p_pkg_list, p_isJSON):
  if not is_repo(p_repo, p_isJSON):
    util.exit_message(p_repo + " is not a valid REPO.", 1, p_isJSON)

  os = util.get_os()

  if os == "el6":
    cmd = "yum --enablerepo=" + p_repo + " install -y"
  elif os == "el7":
    cmd = "yum repo-pkgs " + p_repo + " install -y"
  else:
    cmd = "apt-get install -y"

  for pl in p_pkg_list:
    cmd = cmd + " " + str(pl)
  util.run_sudo(cmd, True, p_isJSON)
  return 0


def remove_packages(p_repo, p_pkg_list, p_isJSON):
  if not is_repo(p_repo, p_isJSON):
    util.exit_message(p_repo + " is not a valid REPO.", 1)

  os = util.get_os()
  if os == "el6":
    cmd = "yum --enablerepo=" + p_repo + " remove -y"
  elif os == "el7":
    cmd = "yum repo-pkgs " + p_repo + " remove -y"
  else:
    cmd = "apt-get remove -y"
  for pl in p_pkg_list:
    cmd = cmd + " " + str(pl)
  util.run_sudo(cmd, True, p_isJSON)
  return 0


## list packages within a repository
def list_packages(p_repo, p_SHOWDUPS, p_isJSON, p_isEXTRA):
  if not is_repo(p_repo, p_isJSON):
    util.exit_message(p_repo + " is not a valid REPO.", 1, p_isJSON)

  [repo_type, name, url, package, key, pkg_filter] = get_repo(p_repo, p_isJSON)

  if not is_installed(p_repo):
    util.exit_message(p_repo + " is not registered.", 1, p_isJSON)

  options = ""
  if p_SHOWDUPS:
    options = "--showduplicates"

  if util.get_os() in APT_LIST:
    return list_apt_packages(p_repo, p_isJSON)

  os = util.get_os()
  if os == "el6":
    cmd = "yum list all | grep " + p_repo
  else:
    cmd = "yum repo-pkgs " + p_repo + " list " + options
  cmd = cmd + " | awk '"

  ## filter package list unless asked to show --extra or --test
  kount = 0
  if not p_isEXTRA:
    for p in pkg_filter:
      kount = kount + 1
      ps = "/" + p.replace('.','\.') + "/"
      if kount > 1:
        cmd = cmd + " || " + ps
      else:
        cmd = cmd + ps

  cmd = "sudo " + cmd + " { print }' | awk '!/debug/ && !/docs/ { print }'"
  outp = util.getoutput(cmd)
  my_logger.info("\n$ " + cmd + "\n\n" + str(outp))

  repoList = []
  for line in outp.splitlines():
    data = line.split()
    if len(data) != 3:
      continue

    repoDict = {}

    p1 = data[0].find('.')
    pkg_nm = data[0][0:p1]
    p2 = data[1].find('.rhel')
    if p2 > 0:
      pkg_ver = data[1][0:p2]
    else:
      pkg_ver = data[1]
    status = ""
    if data[2].startswith("@"):
      status = "Installed"

    repoDict['component'] = pkg_nm
    repoDict['version'] = pkg_ver
    repoDict['status'] = status
    if pkg_nm > "": 
      repoList.append(repoDict)
 
  keys = ['component', 'version', 'status']
  headers = ['Component', 'Version', 'Status']

  if p_isJSON:
    print(json.dumps(repoList, sort_keys=True, indent=2))
  else:
    print(api.format_data_to_table(repoList, keys, headers))

  return(0)


def list_apt_packages(p_repo, p_isJSON):
  cli_ver = get_cli_ver(p_repo)
  raw_list = util.read_file_string(get_apt_repo_file_name())
  repoList = []
  repoDict = {}
  for line in raw_list.splitlines():
    data = line.split()
    if len(data) != 2:
      continue
    if data[0] == "Package:":
      repoDict['component'] = data[1]
    if data[0] == "Version:":
      version = data[1]
      
    if data[0] == "Filename:":
      repoDict['filename'] = data[1]
      p1 =  version.find(".pgdg" + cli_ver)
      if p1 > 0:
        repoDict['version'] = version[0:p1]
        repoList.append(repoDict)
      repoDict = {}

  keys = ['component', 'version']
  headers = ['Component', 'Version']

  if p_isJSON:
    print(json.dumps(repoList, sort_keys=True, indent=2))
  else:
    print(api.format_data_to_table(repoList, keys, headers))

  return(0)


def get_cli_ver(p_repo):
  if p_repo.startswith("xenial"):
    return("16.04")

  if p_repo.startswith("trusty"):
    return("14.04")

  if p_repo.startswith("precise"):
    return("12.4")

  return("")


## process register/unregister REPO command
def process_cmd(p_mode, p_repo, p_isJSON=False):
  if not is_repo(p_repo, p_isJSON):
    util.exit_message(p_repo + " not available.", 1, p_isJSON)

  isInstalled = is_installed(p_repo)

  if p_mode == "register":
    if isInstalled:
      util.exit_message(p_repo + " already registered.", 1, p_isJSON)
    else:
      return(register(p_repo, p_isJSON))

  if p_mode == "unregister":
    if isInstalled:
      return(unregister(p_repo, p_isJSON))
    else:
      util.exit_message(p_repo + " is not registered.", 1, p_isJSON)

  return(0)


## register REPO ###########################################
def register(p_repo, p_isJSON):
  [repo_type, name, url, package, key, repo_filter] = get_repo(p_repo, p_isJSON)

  if util.get_os() in YUM_LIST:
    repo_pkg = url + "/" + package
    util.run_sudo("yum install -y " + repo_pkg, True, p_isJSON)
    return 0

  ## APT ################
  a_file = "/etc/apt/sources.list.d/pgdg.list"
  a_repo = "http://apt.postgresql.org/pub/repos/apt/"
  cmd = '"deb ' + a_repo + ' ' + p_repo + ' main" > ' + a_file
  util.run_sudo("sh -c 'echo " + cmd + "'", True, p_isJSON)

  a_key = "https://www.postgresql.org/media/keys/ACCC4CF8.asc"
  cmd = "wget --quiet -O - " + a_key + " | sudo apt-key add -"
  util.run_sudo(cmd, True, p_isJSON)
  util.run_sudo("apt-get update", True, p_isJSON)
  
  return 0


## unregister REPO #######################################
def unregister(p_repo, p_isJSON):
  [repo_type, name, url, package, key, repo_filter] = get_repo(p_repo, p_isJSON)

  if util.get_os() in YUM_LIST:
    util.run_sudo("yum remove -y " + name, True, p_isJSON)
    return 0

  util.exit_message("UNREGISTER command not supported on this OS", 1, p_isJSON)

