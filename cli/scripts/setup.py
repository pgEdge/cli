#  Copyright 2024-2024 PGEDGE  All rights reserved. #

import os, sys

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire
import util


def pgedge(User, Passwd, db, port=5432, pg="16", spock="latest"):
    """Install pgEdge node (including Postgres, spock, snowflake-sequences and ...)

       Install pgEdge node (including Postgres, spock, snowflake-sequences and ...)
       Example: setup pgedge -U my_user -P my_passwd! -d test --pg 16
       :param User: The database user the will create and own the db
       :param Passwd: The password for the newly created db user 
       :param db: The database name
    """

    print(f"DEBUG {User}, {Passwd}, {db}, {port}, {pg}, {spock}\n")


if __name__ == "__main__":
    fire.Fire(
        {
            "pgedge":         pgedge,
        }
    )
