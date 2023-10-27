import util, db, startup
import os, sys, random, time

thisDir = os.path.dirname(os.path.realpath(__file__))
pg_v = util.get_pg_v(pg)

certd=f"{thisDir}/../../data/{pg_v}/server.crt"

startup.stop_linux("pgcat")
util.echo_cmd("sudo cp pgcat   /usr/local/bin/.")
util.echo_cmd("sudo chmod 755 /usr/local/bin/pgcat")
util.echo_cmd("cp pgcat.toml.template pgcat.toml")

db1 = os.getenv('pgName', 'postgres')
usr = os.getenv('pgeUser', None)
passwd = os.getenv('pgePasswd', None)
prt = int(os.getenv('pgePort', '5432'))


util.echo_cmd(f"sed -i -e \"s/USR/{usr}/g\"       pgcat.toml")
util.echo_cmd(f"sed -i -e \"s/PASSWD/{passwd}/g\" pgcat.toml")
util.echo_cmd(f"sed -i -e \"s/DB/{db}/g\"         pgcat.toml")

util.echo_cmd(f"sed -i -e \"s|CERTD|{certd}|g\"   pgcat.toml")

util.echo_cmd(f"sudo mkdir -p /etc/pgcat/conf")
util.echo_cmd(f"sudo cp pgcat.toml /etc/pgcat/conf/.")

util.echo_cmd(f"sed -i -e \"s/USR/{usr}/g\"       pgcat.service")
util.echo_cmd("sudo cp pgcat.service /etc/systemd/system/.")

startup.reload_linux()
startup.enable_linux("pgcat")

print("Starting PgCat service...")
startup.start_linux("pgcat")

#util.set_column("autostart", "pgcat", "on")
#util.set_column("svcname", "pgcat", "pgcat")

time.sleep(3)
startup.status_linux("pgcat  --lines 0 --no-pager")