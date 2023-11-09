#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import os, sys, json
import fire, libcloud
from libcloud.compute.types import Provider

import util


def get_connection(provider="eqnx", location=None):
    prvdr = provider.lower()
    HOME = os.getenv("HOME")
    sect = util.load_ini(f"{HOME}/mach.ini", prvdr)

    try:
        if prvdr == "eqnx":
            Driver = libcloud.compute.providers.get_driver(Provider.EQUINIXMETAL)
            conn =  Driver(sect['api_token'])
        elif prvdr in ("aws"):
            Driver = libcloud.compute.providers.get_driver(Provider.EC2)
            conn = Driver(sect['access_key_id'], sect['secret_access_key'], region=location)
        else:
            util.exit_message(f"Invalid provider '{prvdr}'")
    except Exception as e:
        util.exit_message(str(e), 1)

    return(prvdr, conn, sect)


def get_location(location):
    prvdr, conn, section = get_connection()

    locations = conn.list_locations()
    for l in locations:
        if l.name.lower() == location.lower():
            return(l)

    return(None)


def get_size(conn, p_size):
    sizes = conn.list_sizes()
    sz = None
    for s in sizes:
        if s.id == p_size:
            return(s)

    util.exit_message(f"Invalid size '{size}'")



def get_image(provider, conn, p_image):
    try:
        if provider == "aws":
            images = conn.list_images(ex_image_ids={p_image})
        else:
            images = conn.list_images()
    except Exception as e:
        util.exit_message(str(e), 1)

    im = None
    for i in images:
        if i.id == p_image:
            return(i)

    util.exit_message(f"Invalid image '{p_image}'")


def get_node(conn, name):

    nodes = conn.list_nodes()
    for n in nodes:
        if n.state in ("terminated", "unknown"):
           continue
        if name == n.name:
            return(n)

    return(None)


def node_destroy(provider, name, location):
    """Destroy a node."""
    node_action("destroy", provider, name, location)
    return


def node_action(action, provider, name, location):
    prvdr, conn, section = get_connection(provider, location)

    nd = get_node(conn, name)
    if nd:
        try:
            if action == "destroy":
                util.message(f"Destroying node '{provider}:{name}:{location}'")
                rc = conn.destroy_node(nd)
            elif action == "stop":
                util.message(f"Stopping node '{provider}:{name}:{location}'")
                rc = conn.stop_node(nd)
            elif action == "start":
                util.message(f"Starting node '{provider}:{name}:{location}'")
                rc = conn.start_node(nd)
            elif action == "reboot":
                util.message(f"Rebooting node '{provider}:{name}:{location}'")
                rc = conn.reboot_node(nd)
            else:
                util.exit_message(f"Invalid action '{action}'")

        except Exception as e:
            util.exit_message(str(e), 1)

        return (rc)

    util.exit_message(f"Node '{provider}:{name}:{location}' not found", 1)


def is_node_unique(name, prvdr, conn, sect):
    if prvdr == "eqnx":
        nodes.conn.list_nodes(sect['project'])
    else:
        nodes = conn.list_nodes()

    for n in nodes:
        if n.name == name:
            return(False)

    return(True)


def node_create(provider, name, location, size=None, image=None, keyname=None, project=None):
    """Create a node."""

    prvdr, conn, sect = get_connection(provider, location)

    if not is_node_unique(name, prvdr, conn, sect):
        util.exit_message(f"Node '{name}' already exists in '{prvdr}:{location}'")

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
        util.exit_message(f"Invalid provider '{prvdr}' (create_node)")

    return


def create_node_aws(name, region, size, image, keyname):
    prvdr, conn, section = get_connection("aws", region)
    sz = get_size(conn, size)
    im = get_image("aws", conn, image)

    try:
        node = conn.create_node(name=name, image=im, size=sz, ex_keyname=keyname)
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def create_node_eqnx(name, location, size, image, project):
    prvdr, conn, section = get_connection("eqnx")
    sz = get_size(conn, size)
    im = get_image("eqnx", conn, image)

    loct = get_location(location)

    try:
        node = conn.create_node(name=name, image=im, size=sz, location=loct, ex_project_id=project)
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def node_start(provider, name, location):
    """Start a node."""
    node_action("start", provider, name, location)
    return


def node_stop(provider, name, location):
    """Stop a node."""
    node_action("stop", provider, name, location)
    return


def node_reboot(provider, name, location):
    """Reboot a node."""
    node_action("reboot", provider, name, location)
    return


def cluster_nodes(node_names, cluster_name, node_ips=None):
    pass


def size_list(provider, location=None):
    """List available node sizes."""
    prvdr, conn, sect = get_connection(provider, location)

    sizes = conn.list_sizes()
    sz = None
    for s in sizes:
        print(f"{s.name.ljust(18)}  {str(round(s.ram / 1024)).rjust(6)}  {str(s.disk).rjust(6)}  {str(s.bandwidth).rjust(6)}  {str(round(s.price, 1)).rjust(5)}")


def location_list(provider, location=None):
    """List available locations."""
    prvdr, conn, sect = get_connection(provider, location)

    locations = conn.list_locations()
    for l in locations:
        print(f"{l.name.ljust(15)} {l.id}")


def node_list(provider, location=None):
    """List nodes."""
    prvdr, conn, sect = get_connection(provider, location)

    if prvdr == "eqnx":
        eqnx_node_list(conn, sect['project'])
    elif prvdr == "aws":
        aws_node_list(conn)
    else:
        util.exit_message(f"Invalid provider '{prvdr}' (node-list)")


def aws_node_list(conn):
    nodes = conn.list_nodes()

    for n in nodes:
        name = n.name.ljust(16)
        try:
            public_ip = n.public_ips[0].ljust(15)
        except Exception as e:
            public_ip = "".ljust(15)
        status = n.state.ljust(10)
        location = n.extra['availability'].ljust(15)
        size = n.extra['instance_type'].ljust(15)
        ##key_name = n.extra['key_name']

        print(f"aws   {name}  {public_ip}  {status}  {location}  {size}")

    return


def eqnx_node_list(conn, project):
    nodes = conn.list_nodes(project)

    for n in nodes:
      name = n.name.ljust(16)
      public_ip = n.public_ips[0].ljust(15)
      size = str(n.size.id).ljust(15)
      ##ram_disk =str(round(n.size.ram / 1024)) + "GB," + str(n.size.disk) + "GB"
      country = str(n.extra['facility']['metro']['country']).lower()
      ##metro = f"{n.extra['facility']['metro']['name']} ({n.extra['facility']['metro']['code']})".ljust(14)
      az = n.extra['facility']['code']
      location = str(f"{country}-{az}").ljust(15)
      status = n.state.ljust(10)
      ##image = n.image.id

      crd = n.extra['facility']['address']['coordinates']
      ##coordinates = f"{round(float(crd['latitude']), 3)},{round(float(crd['latitude']), 3)}"

      print(f"eqnx  {name}  {public_ip}  {status}  {location}  {size}")


def provider_list():
    """List supported cloud providers."""
    print("eqnx  Equinix Metal")
    print("aws   Amazon Web Services")
    return

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
