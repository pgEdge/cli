#!/bin/bash
# this script is used by **ALL** our docker containers
# it has an infinite loop around a bash invocation, so
# if somebody presses CTL-D it doesn't stop the container
# inadvertently.
#

trapKILL() {
  echo ""
  echo ""
  echo "interrupted at `date` - container will exit"
  exit 0
}

trap "trapKILL" KILL


if [ ! -d /tmp/tmp ]; then
  #echo "This container doesn't have a /tmp/tmp directory -something is weird"
  mkdir -p /tmp/tmp
fi

export PS1="DOCKER:\h \W\$ "

if [ -x /usr/local/bin/bootstrap.sh ]; then
  /usr/local/bin/bootstrap.sh
fi


while /bin/true; do
  # ensure that any configs in bashrc get picked up each time bash restarts
  if [ -x ~/.bashrc ]; then
    ~/.bashrc
  fi

  if [ ! -t 1 ]; then
     # this is not a terminal session, so we'd just endlessly loop!!
     echo "Sleeping for a long time (1day), there is no TTY"
     echo "(suggest attaching to this container via 'docker exec ...')"
     sleep 1d
  else
     bash
     echo "`date` : `hostname` If you want to detach, press ^P^Q" |tee -a /tmp/tmp/waiter
     echo "press RETURN to continue"
     read Y
     if [ "$Y" != "" ]; then
        echo "You pressed something else"
        break
     fi
  fi
done

