
import sys, os
import fire


def pre_reqs():
  """Check Pre Requisites for installing pgEdge"""
  pass

def install():
  """Install pgEdge components"""
  pass


def remove(rm_data=False):
  """Remove pgEdge components"""
  pass


def tune():
  """Tune pgEdge components"""
  pass


if __name__ == '__main__':
  fire.Fire({
    'pre-reqs':pre_reqs,
    'install':install,
    'tune':tune,
    'remove':remove,
  })

