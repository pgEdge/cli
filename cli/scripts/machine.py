
#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, sys
import fire, libcloud, util

from libcloud.compute.types import Provider


def get_driver(provider="eqnx"):
    prvdr = provider.lower()
    HOME = os.getenv("HOME")
    sect = util.load_ini(f"{HOME}/mach.ini", prvdr)

    if prvdr == "eqnx":
       drvr =  get_cld_drvr(Provider.EQUINIXMETAL, sect['api_token'])
    elif prvdr in ("aws"):
       drvr =  get_cld_drvr(Provider.EC2, sect['access_key_id'], sect['secret_access_key'])
    else:
       util.exit_message(f"Invalid get-driver() provider ({prvdr})", 1)

    return(prvdr, drvr, sect)


def get_cld_drvr(provider, p1=None, p2=None):
    try:
        cls = libcloud.compute.providers.get_driver(provider)
        drvr = cls(p1, p2)
    except e as Exception:
        util.exit_message(str(e), 1)

    return(drvr)


def get_location(location):
    prvdr, driver, section = get_driver()

    locations = driver.list_locations()
    for l in locations:
        if l.name.lower() == location.lower():
            return(l)

    return(None)


def create(name, location, provider="eqnx", size=None, image=None, project=None):
    prvdr, driver, sect = get_driver(provider)

    if prvdr == "eqnx":
        if size == None:
            size = sect['size']
        if image == None:
            image = sect['image']
        if project == None:
            project = sect['project']

        create_node_eqnx(name, location, size, image, project)

    elif prvdr == "aws":
        if size == None:
            size = sect['size']
        if image == None:
            image = sect['image']
        if project:
            util.exit_message("'project' is not a valid AWS parm", 1)

        create_node_aws(name, location, size, image)

    else:
        util.exit_message(f"Invalid node-create({prvdr}) provider")


def create_node_aws(name, region, size, image):
    prvdr, driver, section = get_driver()

    sizes = driver.list_sizes()
    sz = None
    for s in sizes:
        if s.id == size:
            sz = s
            break

    if sz == None:
        util.exit_message(f"Invalid size {size}")

    images = driver.list_images()

    image = images[0]

    node = driver.create_node(
      name=name,
      image=image,
      size=sz,
      ex_keyname="xyz"
#      ex_securitygroup=SECURITY_GROUP_NAMES,
)


def create_node_eqnx(name, location, size, image, project):
    prvdr, driver, section = get_driver()
    loct = get_location(location)
    if loct == None:
        util.exit_message("Invalid location", 1)

    try:
        node = driver.create_node(name, size, image, loct.id, project)
    except e as Exception:
        util.exit_message(str(e), 1)

    return node.uuid


def cluster_nodes(node_names, cluster_name, node_ips=None):
    pass


def location_list(project):
    driver, section = get_driver()

    locations = driver.list_locations()
    for l in locations:
        print(f"{l.name.ljust(15)} {l.id}")


def list(provider="eqnx"):
    """List nodes."""
    prvdr, driver, sect = get_driver(provider)

    if prvdr == "eqnx":
        eqnx_list(driver, sect['project'])
    elif prvdr == "aws":
        aws_list(driver)
    else:
        util.exit_message(f"Invalid list({prvdr}) provider")


def aws_list(driver):
    nodes = driver.list_nodes()
    for n in nodes:
      name = n.name.ljust(7)
      public_ip = n.public_ips[0].ljust(15)
#      size = n.size.id
#      ram_disk =str(round(n.size.ram / 1024)) + "GB," + str(n.size.disk) + "GB"
#      country = n.extra['facility']['metro']['country']
#      metro = f"{n.extra['facility']['metro']['name']} ({n.extra['facility']['metro']['code']})".ljust(14)
#      az = n.extra['facility']['code'].ljust(4)
      state = n.state
#      image = n.image.id
#
#      crd = n.extra['facility']['address']['coordinates']
#      coordinates = f"{round(float(crd['latitude']), 3)},{round(float(crd['latitude']), 3)}"

      print(f"{name}  {public_ip} {state}")


def eqnx_list(driver, project):
    nodes = driver.list_nodes(project)
    for n in nodes:
      name = n.name.ljust(7)
      public_ip = n.public_ips[0].ljust(15)
      size = n.size.id
      ram_disk =str(round(n.size.ram / 1024)) + "GB," + str(n.size.disk) + "GB"
      country = n.extra['facility']['metro']['country']
      metro = f"{n.extra['facility']['metro']['name']} ({n.extra['facility']['metro']['code']})".ljust(14)
      az = n.extra['facility']['code'].ljust(4)
      state = n.state
      image = n.image.id

      crd = n.extra['facility']['address']['coordinates']
      coordinates = f"{round(float(crd['latitude']), 3)},{round(float(crd['latitude']), 3)}"

      print(f"{name}  {public_ip} {state}  {country}  {metro}  {az}  {coordinates}  {size}  {ram_disk}  {image}")


if __name__ == '__main__':
  fire.Fire({
    'list':       list,
    'create':     create,
    'location-list':   location_list,
  })
