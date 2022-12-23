
import sys, os, json
import util, meta

try:
  import fire
except ImportError as e:
  util.exit_message("Missing 'fire' module from pip", 1)


def gen_self_cert():
  pass


def pg_cert_copy(pg=None):
  pass


def nginx_cert_copy():
  pass


def get_pg_v(pg):
  pg_v = str(pg)

  if pg_v.isdigit():
    pg_v = "pg" + str(pg_v)

  if pg_v == "None":
    k = 0
    pg_s = meta.get_installed_pg()

    for p in pg_s:
      k = k + 1

    if k == 1:
      pg_v = str(p[0])
    else:
      util.exit_message("must be one PG installed", 1)

  if not os.path.isdir(pg_v):
    util.exit_message(str(pg_v) + " not installed", 1)

  rc = os.system(pg_v + "/bin/pg_isready > /dev/null 2>&1")
  if rc != 0:
    util.exit_message(pg_v + " not ready", 1) 

  return(pg_v)

if __name__ == '__main__':
  fire.Fire({
      'gen-self-cert': gen_self_cert,
      'pg-cert-copy': pg_cert_copy,
      'nginx-cert-copy': nginx_cert_copy,
  })


