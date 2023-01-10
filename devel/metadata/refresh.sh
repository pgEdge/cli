set -x 

rm stelthy.db
cat locations.sql | sqlite3 stelthy.db
cat images.sql    | sqlite3 stelthy.db

sqlite3 stelthy.db < select.sql
