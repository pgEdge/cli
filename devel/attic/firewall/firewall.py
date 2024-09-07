#!/usr/bin/env python3

VERSION = 0.1

import sys, os

import fire

import utilx


def fw_info ():
    os = utilx.get_os()
    os_pretty = utilx.get_os_pretty()
    is_apt = utilx.is_apt()
    is_yum = utilx.is_yum()
    hostname = utilx.get_hostname()
    ip = utilx.get_ip()

    print(f"#        os = {os} : {os_pretty}")
    print(f"#    is_apt = {is_apt}")
    print(f"#    is_yum = {is_yum}")
    print(f"#      host = {hostname} : {ip}")
    ##print(f"#  = {}")
    return




if __name__ == "__main__":
    fire.Fire(
        {
            "info":fw_info,
        }
    )

