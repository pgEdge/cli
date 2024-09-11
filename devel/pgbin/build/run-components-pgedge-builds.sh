
bac="./build-all-components.sh"

## build pgedge components
function bpc {
  $bac $1 14 --copy-bin
  rc1=$?
  $bac $1 15 --copy-bin
  rc2=$?
  $bac $1 16 --copy-bin
  rc3=$?
  $bac $1 17 --copy-bin
  rc4=$?

  if [ "$rc1" == "0" ] && [ "$rc2" == "0" ] && [ "$rc3" == "0" ] && [ "$rc3" == "0" ]; then
    return
  fi

  echo "### ERROR: building $bac ####"
  exit 1
}


bpc lolor
bpc spock40
bpc snowflake

bpc spock33

exit 0
