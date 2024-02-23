versions_sql=../../../src/conf/versions.sql
db_local=../../../src/conf/db_local.db

set -x

cp $db_local .
sqlite3 db_local.db < $versions_sql

