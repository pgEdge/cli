
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os

import libcloud
from libcloud.compute.types import Provider

import util, fire


def get_connection(provider="eqnx", metro=None):
    prvdr = provider.lower()
    HOME = os.getenv("HOME")
    sect = util.load_ini(f"{HOME}/mach.ini", prvdr)

    try:
        if prvdr == "eqnx":
            Driver = libcloud.compute.providers.get_driver(Provider.EQUINIXMETAL)
            conn = Driver(sect["api_token"])
        elif prvdr in ("aws"):
            Driver = libcloud.compute.providers.get_driver(Provider.EC2)
            conn = Driver(
                sect["access_key_id"], sect["secret_access_key"], region=metro
            )
        else:
            util.exit_message(f"Invalid provider '{prvdr}'")
    except Exception as e:
        util.exit_message(str(e), 1)

    return (prvdr, conn, sect)


def get_location(location):
    prvdr, conn, section = get_connection()

    locations = conn.list_locations()
    for ll in locations:
        if ll.name.lower() == location.lower():
            return ll

    return None


def get_size(conn, p_size):
    sizes = conn.list_sizes()
    for s in sizes:
        if s.id == p_size:
            return s

    util.exit_message(f"Invalid size '{p_size}'")


def get_image(provider, conn, p_image):
    try:
        if provider == "aws":
            images = conn.list_images(ex_image_ids={p_image})
        else:
            images = conn.list_images()
    except Exception as e:
        util.exit_message(str(e), 1)

    for i in images:
        if i.id == p_image:
            return i

    util.exit_message(f"Invalid image '{p_image}'")


def get_node_values(provider, metro, name):
    prvdr, conn, section = get_connection(provider, metro)
    nd = get_node(conn, name)
    if not nd:
        return None, None, None, None, None
    try:
        name = str(nd.name)
        public_ip = str(nd.public_ips[0])
        status = str(nd.state)
        location = None
        size = None
        if provider == "eqnx":
            country = str(nd.extra["facility"]["metro"]["country"]).lower()
            az = str(nd.extra["facility"]["code"])
            location = str(f"{country}-{az}")
            size = str(nd.size.id)
        else:
            location = nd.extra["availability"]
            size = nd.extra["instance_type"]
    except Exception as e:
        util.exit_message(str(e), 1)

    return (name, public_ip, status, location, size)


def get_node(conn, name):
    nodes = conn.list_nodes()
    for n in nodes:
        if n.state in ("terminated", "unknown"):
            continue
        if name == n.name:
            return n

    return None


def node_destroy(provider, name, metro):
    """Destroy a node."""
    node_action("destroy", provider, name, metro)
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

        return rc

    util.exit_message(f"Node '{provider}:{name}:{location}' not found", 1)


def is_node_unique(name, prvdr, conn, sect):
    if prvdr == "eqnx":
        nodes = conn.list_nodes(sect["project"])
    else:
        nodes = conn.list_nodes()

    for n in nodes:
        if n.name == name:
            return False

    return True


def node_create(
    provider, metro, name, size=None, image=None, keyname=None, project=None
):
    """Create a node."""

    prvdr, conn, sect = get_connection(provider, metro)

    if not is_node_unique(name, prvdr, conn, sect):
        util.exit_message(f"Node '{name}' already exists in '{prvdr}:{metro}'")

    if prvdr == "eqnx":
        if size is None:
            size = sect["size"]
        if image is None:
            image = sect["image"]
        if project is None:
            project = sect["project"]

        create_node_eqnx(name, metro, size, image, project)

    elif prvdr == "aws":
        if size is None:
            size = sect["size"]
        if image is None:
            my_image = f"image-{metro}"
            print(sect)
            image = sect[my_image]
        if keyname is None:
            keyname = sect["keyname"]
        if project:
            util.exit_message("'project' is not a valid AWS parm", 1)

        create_node_aws(name, metro, size, image, keyname)

    else:
        util.exit_message(f"Invalid provider '{prvdr}' (create_node)")

    return


def create_node_aws(name, region, size, image, keyname):
    prvdr, conn, section = get_connection("aws", region)
    sz = get_size(conn, size)
    im = get_image("aws", conn, image)

    try:
        conn.create_node(name=name, image=im, size=sz, ex_keyname=keyname)
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def create_node_eqnx(name, location, size, image, project):
    prvdr, conn, section = get_connection("eqnx")
    sz = get_size(conn, size)
    im = get_image("eqnx", conn, image)

    loct = get_location(location)

    try:
        conn.create_node(
            name=name, image=im, size=sz, location=loct, ex_project_id=project
        )
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def node_start(provider, name, metro):
    """Start a node."""
    node_action("start", provider, name, metro)
    return


def node_stop(provider, name, metro):
    """Stop a node."""
    node_action("stop", provider, name, metro)
    return


def node_reboot(provider, name, metro):
    """Reboot a node."""
    node_action("reboot", provider, name, metro)
    return


def cluster_nodes(cluster_name, providers, metros, node_names):
    """Create a Cluster definition json file from a set of nodes."""

    util.message(
        f"\n# cluster-nodes(cluster_name={cluster_name}, providers={providers}, metros={metros}, node_names={node_names})"
    )

    if not isinstance(providers, list) or len(providers) < 2:
        util.exit_message(
            f"providers parm '{providers}' must be a square bracketed list with two or more elements",
            1,
        )

    if not isinstance(metros, list) or len(metros) < 2:
        util.exit_message(
            f"metros parm '{metros}' must be a square bracketed list with two or more elements",
            1,
        )

    if not isinstance(node_names, list) or len(node_names) < 2:
        util.exit_message(
            f"node_names parm '{node_names}' must be a square bracketed list with two or more elements",
            1,
        )

    if (not len(providers) == len(metros)) or (not len(providers) == len(node_names)):
        s1 = f"providers({len(providers)}), metros({len(metros)}), and node_names({len(node_names)})"
        util.exit_message(f"{s1} parms must have same number of elements")

    if len(node_names) != len(set(node_names)):
        util.exit_message(f"node_names ({node_names}) must be unique")

    node_kount = len(providers)
    i = 0
    while i < node_kount:
        util.message(f"\n## {providers[i]}, {metros[i]}, {node_names[i]}")
        prvdr, conn, section = get_connection(providers[i], metros[i])

        name, public_ip, status, metro, size = get_node_values(
            providers[i], metros[i], node_names[i]
        )
        if not name:
            util.exit_message(
                f"Node ({providers[i]}, {metros[i]}, {node_names[i]}) not available"
            )

        util.message(f"### {name}, {public_ip}, {status}, {metro}, {size}")

        i = i + 1

    # n1 = get_node(providers[0], locations[0], node_names[0])
    # n2 = get_node(providers[1], locations[1], node_names[1])
    return


def size_list(provider, location=None):
    """List available node sizes."""
    prvdr, conn, sect = get_connection(provider, location)

    sizes = conn.list_sizes()
    for s in sizes:
        price = s.price
        if price is None:
            price = 0
        ram = s.ram
        if ram is None:
            ram = 0
        bandwidth = s.bandwidth
        if bandwidth is None or str(bandwidth) == "0":
            bandwidth = ""
        print(
            f"{str(s.id).ljust(35)} {str(round(ram / 1024)).rjust(6)}  {str(s.disk).rjust(6)}  \
              {str(bandwidth).rjust(6)} {str(round(price, 1)).rjust(5)}"
        )


def location_list(provider, location=None):
    """List available locations."""
    prvdr, conn, sect = get_connection(provider, location)

    locations = conn.list_locations()
    for ll in locations:
        print(f"{ll.name.ljust(15)} {ll.id}")


def node_list(provider, location=None):
    """List nodes."""
    prvdr, conn, sect = get_connection(provider, location)

    if prvdr == "eqnx":
        eqnx_node_list(conn, sect["project"])
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
        except Exception:
            public_ip = "".ljust(15)
        status = n.state.ljust(10)
        location = n.extra["availability"].ljust(15)
        size = n.extra["instance_type"].ljust(15)
        # key_name = n.extra['key_name']

        print(f"aws   {name}  {public_ip}  {status}  {location}  {size}")

    return


def eqnx_node_list(conn, project):
    nodes = conn.list_nodes(project)

    for n in nodes:
        name = n.name.ljust(16)
        public_ip = n.public_ips[0].ljust(15)
        size = str(n.size.id).ljust(15)
        # ram_disk =str(round(n.size.ram / 1024)) + "GB," + str(n.size.disk) + "GB"
        country = str(n.extra["facility"]["metro"]["country"]).lower()
        # metro = f"{n.extra['facility']['metro']['name']} ({n.extra['facility']['metro']['code']})".ljust(14)
        az = n.extra["facility"]["code"]
        location = str(f"{country}-{az}").ljust(15)
        status = n.state.ljust(10)
        # image = n.image.id

        # crd = n.extra["facility"]["address"]["coordinates"]
        # coordinates = f"{round(float(crd['latitude']), 3)},{round(float(crd['latitude']), 3)}"

        print(f"eqnx  {name}  {public_ip}  {status}  {location}  {size}")


def provider_list():
    """List supported cloud providers."""
    print("eqnx  Equinix Metal")
    print("aws   Amazon Web Services")
    return


if __name__ == "__main__":
    fire.Fire(
        {
            "node-create": node_create,
            "node-start": node_start,
            "node-stop": node_stop,
            "node-reboot": node_reboot,
            "node-destroy": node_destroy,
            "node-list": node_list,
            "cluster-nodes": cluster_nodes,
            "provider-list": provider_list,
            "location-list": location_list,
            "size-list": size_list,
        }
    )
