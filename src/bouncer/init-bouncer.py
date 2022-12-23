import component, util, os

MY_HOME = os.getenv('MY_HOME')
ini_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'pgbouncer.ini'
util.replace('MY_HOME', MY_HOME, ini_file, True)

component.init_comp('bouncer', 'pgbouncer.pid')

