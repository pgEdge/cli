
import sys, os
import fire
import util


def pre_reqs():
  """Check Pre Requisites for installing pgEdge"""
  pass

def install(User=None, Password=None, database=None, Country='??', port=5432, autostart=False):
  """Install pgEdge components"""
  pass


def remove(rm_data=False):
  """Remove pgEdge components"""
  pass


def tune(component="pg15"):
  """Tune pgEdge components"""

  if not os.path.isdir(component):
    util.exit_message(f"{component} is not installed", 1)

  rc = os.system("./nodectl tune " + component)
  return(rc)


if __name__ == '__main__':
  fire.Fire({
    'pre-reqs':pre_reqs,
    'install':install,
    'tune':tune,
    'remove':remove,
  })

