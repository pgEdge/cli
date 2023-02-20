
import sys, os
import fire


def run_cmd(p_cmd, p_comp=None):
  nc_cmd = "./nodectl " + p_cmd
  if p_comp:
    nc_cmd = nc_cmd + " " + p_comp
  rc = os.system(nc_cmd)
  return(rc)


def list():
  """Display available/installed components"""

  run_cmd('list')


def update():
  """Retrieve new list of components & update this software"""

  run_cmd('update')


def upgrade(component):
  """Perform an upgrade  to a newer version of a component"""

  run_cmd('upgrade', component)


def config(component):
  """Configure a component"""

  run_cmd('config', component)


def init(component):
  """Initialize a component"""

  run_cmd('init', component)


def clean():
  """Delete downloaded component files from local cache"""

  run_cmd('clean')


if __name__ == '__main__':
  fire.Fire({
    'list':list,
    'update':update,
    'upgrade':upgrade,
    'config':config,
    'init':init,
    'clean':clean,
  })

