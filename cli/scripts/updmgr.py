
import sys, os
import fire

def install():
  pass

def remove():
  pass

def tune():
  pass


if __name__ == '__main__':
  fire.Fire({
    'install':install,
    'remove':remove,
    'tune':tune,
  })

