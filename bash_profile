# STELTHY-IO for ~/.bash... ############################################################
alias git-push="cd ~/dev/ndctl; git status; git add .; git commit -m wip; git push"
alias bp="cd ~/dev/ndctl; . ./bp.sh"
alias ver="vi ~/dev/ndctl/src/conf/versions.sql"

export REGION=us-east-2
export BUCKET=s3://pgedge-download

export DEV=$HOME/dev
export IN=$DEV/in
export OUT=$DEV/out
export HIST=$DEV/history
export ND=$DEV/ndctl
export SRC=$IN/sources
export BLD=/opt/pgbin-build/pgbin/bin

export ND_NO_AUTO_UPDATE=1
export DEVEL=$ND/devel
export PG=$DEVEL/pg
export CLI=$ND/cli/scripts
export REPO=http://localhost:8000

export JAVA_HOME=/etc/alternatives/jre_11_openjdk

export PATH=/usr/local/bin:$JAVA_HOME/bin:$PATH

