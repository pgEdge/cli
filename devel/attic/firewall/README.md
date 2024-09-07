# firewall-cli

This intended to be a contrib module to this CLI someday soon.
It will be a simple/powerful little script that figures out
enviornment you are in and it then allows for a consistent
UI to query and change the firewall
   
Example of supported firewalls for v1.0 includes:

  fwd - firewalld (default firewall for EL)
  ufw - default Ubuntu firewall
  aws - ec2 security group for a vm
  gcp - security group for a GCP vm
  azr - security group for an AZURE vm


example commands are:
  install() - in the cloud there is usually always a vendor firewall
  remove() - removing a firewall in to cloud throws a warning then disables
  info() - consistent format that's easy to understand
  enable()
  disable()
  start()
  stop()
  is_active() - Is there an active firewall
  get_blocked_ports() -
  block_port(ip, port)
  unblock_port(ip, port)


