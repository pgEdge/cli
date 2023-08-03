
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
  """Update nodectl with a new list of available components"""

  run_cmd('update')


def install(component):
  """Install a component"""

  run_cmd('install', component)


def remove(component):
  """Uninstall a component"""

  run_cmd('remove', component)


def upgrade(component):
  """Perform an upgrade  to a newer version of a component"""

  run_cmd('upgrade', component)


def downgrade(component):
  """Perform a downgrade to an older version of a component"""

  run_cmd('downgrade', component)


def clean():
  """Delete downloaded component files from local cache"""

  run_cmd('clean')


def install_pgedge(User=None, Passwd=None, db=None, tenancy='Single', leader='False', customer_id=None):
    """
    './nc um install-pgedge' is a proposed wrapper for './nc install pgedge'

  Proposed wrapper for './nc install pgedge'

      New fields are:
        tenancy:     defaults to 'Single' and optionally can be set to 'Multi'
        leader:      defaults to 'False' and optionally can be set to 'True'
        customer_id: defaults to None and MUST BE VALID if provided

      New EditChecks are:
        if tenancy == 'Multi':
          'customer_id' must be VALIDated
          'User' & 'db' must not be specified (& are set to u-{customer_id} & d-{customer_id})
          'leader' will overridden & be set to 'False'

        if leader == 'True':
          'tenancy' must be 'Single'
          --pgcat & --patroni & --backrest flags will be overridden & set to 'True'   
    """


if __name__ == '__main__':
  fire.Fire({
    'list':list,
    'update':update,
    'install':install,
    'remove':remove,
    'upgrade':upgrade,
    'install-pgedge':install_pgedge,
    'clean':clean,
  })
