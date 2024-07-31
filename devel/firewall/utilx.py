
# Copyright (C) 2023-2024 Denis L. Lussier #

import os, sys, platform, socket    


VERSION = 0.1

VALID_OS = [ "el8", "el9", "el10", "ub22", "ub24", "db11", "db12" ]


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


def get_hostname():
    return(platform.node())


def get_os():
    rf = "/etc/redhat-release"
    if os.path.exists(rf):
        rc = os.system(f'grep "platform:el9" {rf} > /dev/null 2>&1')
        if rc == 0:
            return "el9"

        rc = os.system(f'grep "platform:el8" {rf} > /dev/null 2>&1')
        if rc == 0:
            return "el8"

    rf = "/etc/os-release"
    if os.path.exists(rf):
        rc = os.system(f'grep "22.04" {rf} > /dev/null 2>&1')
        if rc == 0:
            return "ub22"

        rc = os.system(f'grep "24.04" {rf} > /dev/null 2>&1')
        if rc == 0:
            return "ub24"

    return("?")


def get_ip():
    cmd = 'ip address | grep inet | grep "\/24" | head -1'
    ip_line = get_output(cmd)

    cmd = f'echo "{ip_line}" | cut -d " " -f 2 | cut -f1 -d"/"'
    ##print(f"DEBUG {cmd}")
    return(get_output(cmd))



def get_os_pretty():
    pretty_os = "?"
    rf = "/etc/os-release"

    if os.path.exists(rf):
        pretty_os = get_output(
           f"cat {rf} | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'")

    return(pretty_os)


def get_output(p_cmd):
    from subprocess import check_output

    try:
        out = check_output(p_cmd, shell=True)
        return out.strip().decode("ascii")
    except Exception:
        return "??"



