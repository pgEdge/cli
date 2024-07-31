#!/usr/bin/env python3

VERSION = 0.1

import sys, os

import fire

import utilx


def fw_info ():
    os = utilx.get_os()
    is_apt = utilx.is_apt()
    is_yum = utilx.is_yum()

    print(f"#     os={os}")
    print(f"# is_apt={is_apt}")
    print(f"# is_yum={is_yum}")
    return




if __name__ == "__main__":
    fire.Fire(
        {
            "info":fw_info,
        }
    )

