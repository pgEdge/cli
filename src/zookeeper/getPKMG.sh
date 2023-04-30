
## Determine the Package Manager (PKMG) & OS Major Version (VER_OS)

export OS=`uname`

if [[ "$OS" == "Darwin" ]]; then
  export PKGM=brew
  export PLATFORM=osx

elif [[ "$OS" == "Linux" ]]; then
  yum --version > /dev/null 2>&1
  rc=$?
  if [ "$rc" == "0" ]; then
    export PKMG=yum
    export PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
    export VER_OS=`cat /etc/os-release | grep VERSION_ID | cut -d= -f2 | tr -d '\"'`
  else
    export PKMG=apt
    export VER_OS=`lsb_release -cs`
  fi

else
  echo "$OS not supported"
  exit 1
fi

