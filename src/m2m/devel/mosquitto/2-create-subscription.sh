
set -x


if [ "$1" == "" ]; then
  source ./env.sh
else
  env_file="$1"
  if [ -f "$env_file" ]; then
    source "$env_file"
  else
    echo "ERROR:"
    exit 1
  fi
fi

mosquitto_sub -v -h $BROKER_HOST -p $BROKER_PORT -t $TOPIC

