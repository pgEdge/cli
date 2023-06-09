#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""Starfleet is for leveraging the secure pgEdge Cloud"""

import os, sys, random, time, json, socket, subprocess, re
import util, fire, meta, cluster


def get_token(client_id, client_secret):
  pass

def create_cluster(cluster_nm, User, Passwd, DB):
  pass

def get_nodes(cluster, lattitude=None, longitude=None, order_by=None):
  pass 


if __name__ == '__main__':
  fire.Fire({
    'get-token':      get_token,
    'create-cluster': create_cluster,
    'get-nodes':      get_nodes 
  })
