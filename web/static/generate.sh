
sqlite3 local.db < ../../src/conf/components.sql
sqlite3 local.db < ../../src/conf/versions.sql

python3 components.py > html/index.html
python3 about.py > html/about.html
python3 services.py > html/services.html
python3 usage.py > html/usage.html
python3 tutorial.py > html/tutorial.html

