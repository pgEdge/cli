
import sys, os
import fire

#  list      - Display available/installed components 
#  update    - Retrieve new lists of components
#  upgrade   - Perform an upgrade of a component
#  config    - Configure a component
#  init      - Initialize a component
#  clean     - Delete downloaded component files from local cache

def install():
#  install   - Install (or re-install) a component  
  pass

def remove():
#  remove    - Un-install component   
  pass

def tune():
  pass


if __name__ == '__main__':
  fire.Fire({
    'install':install,
    'remove':remove,
    'tune':tune,
  })

