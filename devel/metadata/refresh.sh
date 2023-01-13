set -x 

psql -f locations.sql
psql -f flavors.sql

#psql -f select.sql

