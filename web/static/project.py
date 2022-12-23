import sqlite3, sys, os

def page_hdr (proj, descrip, homepage):
  print(f"<h2>{proj} <font size=-1>{descrip} ({homepage})</h2>")


def table_top (caption, border):
  print(f"<table border={border}>")
  print(f"  <caption><b>{caption}</b></caption>")
  print(f"  <tr><th width=65>Version</th><th width=75>Rel Date</th><th></th></tr>")


def table_rows (ver, rel_dt, notes):
  print(f"  <tr><td>v{ver}</td><td>{rel_dt}</td><td><font size=-1>{notes}</font></td></tr>")


def table_bottom ():
  print("</table>")




##################################################################
#   MAINLINE
##################################################################
con = sqlite3.connect("local.db")
c = con.cursor()

page_hdr("pgredis", "Blah, Blah...", "<a href=http://pgsql.io/pgredis>PgRedis</a>")
table_top("Release History", 1)
table_rows("1.2.3", "28Mar66", "<a href=https://notes.io>Notes</a>")
table_rows("1.2.2", "28Mar65", "")
table_bottom()

