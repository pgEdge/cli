
import sys, os
import fire


def start():
  """Start server components"""
  pass


def stop():
  """Stop server components"""
  pass


def status():
  """Display running status of installed server components"""
  pass


def restart():
  """Stop & then start server components"""
  pass


def reload():
  """Reload server configuration files (without a restart)"""


def enable():
  """Enable a component"""
  pass


def disable():
  """Disable a server component from starting automatically"""
  pass


if __name__ == '__main__':
  fire.Fire({
    'start':start,
    'stop':stop,
    'status':status,
    'restart':restart,
    'reload':reload,
    'enable':enable,
    'disable':disable,
  })

