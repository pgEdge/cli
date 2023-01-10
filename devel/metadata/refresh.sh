set -x 

psql -f locations.sql
psql -f images.sql

#psql -f select.sql

