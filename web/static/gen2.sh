
genPage () {
  echo "genPage($1)"
  python3 $1.py
}

sqlite3 local.db < ../../src/conf/components.sql
sqlite3 local.db < ../../src/conf/ver2.sql 

rm html/*.html

genPage index
genPage contact_us
genPage about
genPage services
genPage downloads
genPage tutorial

genPage components

