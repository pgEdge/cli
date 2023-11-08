import json
#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, sys
import fire, libcloud, util

from libcloud.compute.types import Provider

def get_driver(provider="eqnx", location=None):
    prvdr = provider.lower()
    HOME = os.getenv("HOME")
    sect = util.load_ini(f"{HOME}/mach.ini", prvdr)

    try:
        if prvdr == "eqnx":
            cls = libcloud.compute.providers.get_driver(Provider.EQUINIXMETAL)
            drvr =  cls(sect['api_token'])
        elif prvdr in ("aws"):
            cls = libcloud.compute.providers.get_driver(Provider.EC2)
            drvr = cls(sect['access_key_id'], sect['secret_access_key'], region=location)
        else:
            util.exit_message(f"Invalid provider '{prvdr}'")
    except Exception as e:
        util.exit_message(str(e), 1)

    return(prvdr, drvr, sect)


def get_location(location):
    prvdr, driver, section = get_driver()

    locations = driver.list_locations()
    for l in locations:
        if l.name.lower() == location.lower():
            return(l)

    return(None)


def get_size(driver, p_size):
    sizes = driver.list_sizes()
    sz = None
    for s in sizes:
        if s.id == p_size:
            return(s)

    util.exit_message(f"Invalid size '{size}'")



def get_image(provider, driver, p_image):
    try:
        if provider == "aws":
            images = driver.list_images(ex_image_ids={p_image})
        else:
            images = driver.list_images()
    except Exception as e:
        util.exit_message(str(e), 1)

    im = None
    for i in images:
        if i.id == p_image:
            return(i)

    util.exit_message(f"Invalid image '{p_image}'")


def node_destroy(provider, name, location):
    """Destroy a node."""

    prvdr, driver, section = get_driver(provider, location)

    nodes = driver.list_nodes()
    for n in nodes:
        if n.state in ("terminated", "unknown"):
           continue
        if name == n.name:
            util.message(f"Destroying {provider} node {name}")
            if driver.destroy_node(n):
                return(0)

    util.exit_message(f"{provider} node {name} not found", 1)
    return


def node_create(provider, name, location, size=None, image=None, keyname=None, project=None):
    """Create a node."""

    prvdr, driver, sect = get_driver(provider, location)

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
        if keyname == None:
            keyname = sect['keyname']
        if project:
            util.exit_message("'project' is not a valid AWS parm", 1)

        create_node_aws(name, location, size, image, keyname)

    else:
        util.exit_message(f"Invalid provider '{prvdr}' (create)")


def create_node_aws(name, region, size, image, keyname):
    prvdr, driver, section = get_driver("aws", region)
    sz = get_size(driver, size)
    im = get_image("aws", driver, image)

    try:
        node = driver.create_node(name=name, image=im, size=sz, ex_keyname=keyname)
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def create_node_eqnx(name, location, size, image, project):
    prvdr, driver, section = get_driver("eqnx")
    sz = get_size(driver, size)
    im = get_image("eqnx", driver, image)

    loct = get_location(location)

    try:
        node = driver.create_node(name=name, image=im, size=sz, location=loct, ex_project_id=project)
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def node_start():
    """Start a node."""
    pass


def node_stop():
    """Stop a node."""
    pass


def node_reboot():
    """Reboot a node."""
    pass


def cluster_nodes(node_names, cluster_name, node_ips=None):
    pass


def size_list(provider, location=None):
    """List available node sizes."""

    prvdr, driver, sect = get_driver(provider, location)

    sizes = driver.list_sizes()
    sz = None
    for s in sizes:
        print(f"{s.name.ljust(18)}  {str(round(s.ram / 1024)).rjust(6)}  {str(s.disk).rjust(6)}  {str(s.bandwidth).rjust(6)}  {str(round(s.price, 1)).rjust(5)}")


def location_list(provider, location=None):
    """List available locations."""

    prvdr, driver, sect = get_driver(provider, location)

    locations = driver.list_locations()
    for l in locations:
        print(f"{l.name.ljust(15)} {l.id}")


def node_list(provider, location=None):
    """List nodes."""
    prvdr, driver, sect = get_driver(provider, location)

    if prvdr == "eqnx":
        eqnx_node_list(driver, sect['project'])
    elif prvdr == "aws":
        aws_node_list(driver)
    else:
        util.exit_message(f"Invalid provider '{prvdr}' (node-list)")


def aws_node_list(driver):
    nodes = driver.list_nodes()
    for n in nodes:
        name = n.name.ljust(7)
        try:
            public_ip = n.public_ips[0].ljust(15)
        except Exception as e:
            public_ip = "".ljust(15)
        state = n.state.ljust(10)
        location = n.extra['availability']
        size = n.extra['instance_type'].ljust(12)
        key_name = n.extra['key_name']

        print(f"aws   {name}  {public_ip}  {state}  {location}  {size}  {key_name}")

    return


def eqnx_node_list(driver, project):
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

      print(f"eqnx  {name}  {public_ip} {state}  {country}  {metro}  {az}  {coordinates}  {size}  {ram_disk}  {image}")


def provider_list():
    """List supported cloud providers."""

    print("eqnx  Equinix Metal")
    print("aws   Amazon Web Services")


if __name__ == '__main__':
  fire.Fire({
    'node-create':     node_create,
    'node-start':      node_start,
    'node-stop':       node_stop,
    'node-reboot':     node_reboot,
    'node-destroy':    node_destroy,
    'node-list':       node_list,
    'provider-list':   provider_list,
    'location-list':   location_list,
    'size-list':       size_list,
  })
