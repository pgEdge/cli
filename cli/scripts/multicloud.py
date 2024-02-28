#!/usr/bin/env python3

#  Copyright 2023-2024 PGEDGE  All rights reserved. #

import os, sys, configparser, sqlite3

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import fire
import libcloud
import util
import cluster

import termcolor
from libcloud.compute.types import Provider
from prettytable import PrettyTable

CONFIG = f"{os.getenv('HOME')}/.multicloud.conf"

PROVIDERS = \
    [
        ["akm", "linode",       "Akamai Linode"],
        ["eqn", "equinixmetal", "Equinix Metal"],
        ["aws", "ec2",          "Amazon Web Services"],
        ["azr", "azure",        "Microsoft Azure"],
        ["gcp", "gce",          "Google Cloud Platform"],
    ]


def get_location(provider, location):
    conn, section, region, airport, project = get_connection(provider)

    locations = conn.list_locations()
    for ll in locations:
        if ll.name.lower() == location.lower():
            return ll

    return None

def get_key(conn, p_key):
    keys = conn.list_key_pairs()
    for k in keys:
        if k.name == p_key:
            return k.public_key

    util.exit_message(f"Invalid key '{p_key}'")


def get_size(conn, p_size):
    sizes = conn.list_sizes()
    for s in sizes:
        if s.id == p_size:
            return s

    util.exit_message(f"Invalid size '{p_size}'")


def get_image(provider, conn, p_image):
    try:
        if provider in ("ec2", "aws"):
            images = conn.list_images(ex_image_ids={p_image})
        else:
            images = conn.list_images()
    except Exception as e:
        util.exit_message(str(e), 1)

    for i in images:
        if i.id == p_image:
            return i

    util.exit_message(f"Invalid image '{p_image}'")


def get_node_values(provider, region, name):
    conn, section, region, airport, project = get_connection(provider, region)
    nd = get_node(conn, name)

    if not nd:
        return None, None, None, None, None

    try:
        name = str(nd.name)
        public_ip = str(nd.public_ips[0])
        status = str(nd.state)
        location = None
        size = None
        if provider in ("eqn", "equinixmetal"):
            country = str(nd.extra["facility"]["metro"]["country"]).lower()
            zone = str(nd.extra["facility"]["code"])
            size = str(nd.size.id)
        else:
            zone = ""
            instance_type = ""

            try:
                zone = nd.extra["availability"]
            except Exception:
                pass

            try:
                size = nd.extra["instance_type"]
            except Exception:
                pass
    except Exception as e:
        util.exit_message(str(e), 1)

    return (name, public_ip, status, zone, size)


def get_node(conn, name):
    nodes = conn.list_nodes()
    for n in nodes:
        if n.state in ("terminated", "unknown"):
            continue
        if name == n.name:
            return n

    return None


def node_action(action, provider, airport, name):
    region = get_region(provider, airport)
    conn, section, region, airport, project = get_connection(provider, region)

    nd = get_node(conn, name)
    if nd:
        try:
            if action == "destroy":
                util.message(f"Destroying node '{provider}:{region}:{name}'")
                rc = conn.destroy_node(nd)
            elif action == "stop":
                util.message(f"Stopping node '{provider}:{region}:{name}'")
                rc = conn.stop_node(nd)
            elif action == "start":
                util.message(f"Starting node '{provider}:{region}:{name}'")
                rc = conn.start_node(nd)
            elif action == "reboot":
                util.message(f"Rebooting node '{provider}:{region}:{name}'")
                rc = conn.reboot_node(nd)

        except Exception as e:
            util.exit_message(str(e), 1)

        return rc

    util.exit_message(f"Node '{provider}:{region}:{name}' not found", 1)


def is_node_unique(name, prvdr, conn, sect):
    if prvdr in ("eqn", "equinixmetal"):
        project = sect["project"]
        nodes = conn.list_nodes(project)
    else:
        nodes = conn.list_nodes()

    for n in nodes:
        if n.name == name:
            return False

    return True


def create_node(
    provider, airport, name, size=None, image=None, ssh_key=None, project=None
):
    """Create a virtual machine (VM)."""

    region = get_region(provider, airport)
    if region:
       util.message(f"  # ({provider}, {airport}) --> {region}")
    else:
       util.exit_message(f"Invalid provider:airport '{provider}:{airport}'")

    conn, sect, region, airport, project = get_connection(provider, region, project)

    if not is_node_unique(name, provider, conn, sect):
        util.exit_message(f"Node '{name}' already exists in '{provider}:{region}'")

    if provider in ("eqn", "equinixmetal"):
        if size is None:
            size = sect["size"]
        if image is None:
            image = sect["image"]
        if project is None:
            project = sect["project"]

        create_node_eqn(name, region, size, image, project)

    elif provider in ("akm", "linode"):
        if size is None:
            size = sect["size"]
        if image is None:
            image = sect["image"]
        if ssh_key is None:
            ssh_key = sect["ssh_key"]
        if project:
            util.exit_message("'project' is not a valid AKM parm", 1)

        create_node_akm(name, region, size, image, ssh_key)
                        
    elif provider in ("aws", "ec2"):
        if size is None:
            size = sect["size"]
        if image is None:
            my_image = f"image-{region}"
            try:
                image = sect[my_image]
            except Exception:
                util.exit_message(f"Missing image-id for '{region}'")
        if ssh_key is None:
            ssh_key = sect["ssh_key"]
        if project:
            util.exit_message("'project' is not a valid AWS parm", 1)

        create_node_aws(name, region, size, image, ssh_key)

    return


def create_node_aws(name, region, size, image, ssh_key):
    conn, section, region, airport, project = get_connection("ec2", region)
    sz = get_size(conn, size)
    im = get_image("aws", conn, image)

    try:
        nd = conn.create_node(name=name, image=im, size=sz, ex_keyname=ssh_key)
        print(f"node.id = {nd.id}")
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def create_node_akm(name, region, size, image, ssh_key):
    conn, aaa, bbb, ccc, ddd = get_connection("akm")
    sz = get_size(conn, size)
    im = get_image("eqn", conn, image)
    lctn = get_location("akm", region)
    key = get_key(conn, ssh_key)

    try:
        conn.create_node(
            name=name, image=im, size=sz, root_pass="AbcDDD1234!!!!!", location=lctn, ex_authorized_keys=[key]
        )
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def create_node_eqn(name, location, size, image, project):
    conn, section, region, airport, project = get_connection("equinixmetal")
    sz = get_size(conn, size)
    im = get_image("eqn", conn, image)
    loct = get_location("eqn", location)

    try:
        conn.create_node(
            name=name, image=im, size=sz, location=loct, ex_project_id=project
        )
    except Exception as e:
        util.exit_message(str(e), 1)

    return


def start_node(provider, airport, node_name):
    """Start a VM."""
    node_action("start", provider, airport, node_name)
    return


def stop_node(provider, airport, node_name):
    """Stop a VM."""
    node_action("stop", provider, airport, node_name)
    return


def reboot_node(provider, airport, node_name):
    """Reboot a VM."""
    node_action("reboot", provider, airport, node_name)
    return


def destroy_node(provider, airport, node_name):
    """Destroy a node."""
    node_action("destroy", provider, airport, node_name)
    return


def list_keys(provider, region=None, project=None):
    """List available SSH Keys (not working for Equinix)."""
    conn, sect, region, airport, project = get_connection(provider, region, project)
    keys = conn.list_key_pairs()
    for k in keys:
       print(k)


def list_sizes(provider, region=None, project=None):
    """List available node sizes."""
    conn, sect, region, airport, project = get_connection(provider, region, project)

    if region is None:
        region = ""

    sizes = conn.list_sizes()
    sl = []
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
        cpu = ""
        if provider in ("aws", "ec2"):
            cpu = s.extra["vcpu"]
        elif provider in ("eqn", "equinixmetal"):
            cpu = s.extra["cpus"]
        elif provider == "akm":
            cpu = s.extra["vcpus"]
        if cpu is None:
            cpu = ""
        sl.append([provider, region, s.id, cpu, round(ram/1024), s.disk, bandwidth, price])

    p = PrettyTable()
    p.field_names = ["Provider", "Region", "Size", "CPU", "RAM", "Disk", "Bandwidth", "Price"]
    p.add_rows(sl)
    p.float_format = ".2"
    p.align["Size"] = "l"
    p.align["RAM"] = "r"
    p.align["Disk"] = "r"
    p.align["Bandwidth"] = "r"
    p.align["Price"] = "r"
    print(p)


def list_nodes(provider, region=None, project=None):
    """List virtual machines."""
    conn, sect, region, airport, project = get_connection(provider, region, project)

    nl = []
    if provider == "eqn":
        nl = eqn_node_list(conn, region, project)
    elif provider == "aws":
        nl = aws_node_list(conn, region)
    elif provider == "akm":
        nl = akm_node_list(conn, region)
    else:
        util.exit_message(f"Invalid provider '{provider}' (list_nodes)")

    p = PrettyTable()
    p.field_names = ["Provider", "Airport", "Node", "Status", "Size", "Country", "Region", "Zone", "Public IP", "Private IP"]
    p.align["Node"] = "l"
    p.align["Size"] = "l"
    p.align["Public IP"] = "l"
    p.align["Private IP"] = "l"
    p.align["Region"] = "l"
    p.add_rows(nl)
    print(p)

    return


def akm_node_list(conn, region):
    try:
        nodes = conn.list_nodes()
    except Exception as e:
        util.exit_message(str(e), 1)

    nl = []
    for n in nodes:
        node = n.name

        try:
            public_ip = n.public_ips[0]
        except Exception:
            public_ip = ""

        try:
            private_ip = n.private_ip[0]
        except Exception:
            private_ip = ""

        status = n.state
        region = n.extra["location"]
        zone = ""
        size = n.size
        country = region[:2]
        key_name = ""
        airport = get_airport("akm", region)
        nl.append(["akm", airport, node, status, size, country, region, zone, public_ip, private_ip])

    return(nl)


def aws_node_list(conn, region):
    try:
        nodes = conn.list_nodes()
    except Exception as e:
        util.exit_message(str(e), 1)

    nl = []
    for n in nodes:
        node = n.name
        try:
            public_ip = n.public_ips[0]
        except Exception:
            public_ip = ""
        try:
            private_ip = n.private_ip[0]
        except Exception:
            private_ip = ""
        status = n.state
        zone = n.extra["availability"]
        size = n.extra["instance_type"]
        country = region[:2]
        key_name = n.extra['key_name']
        airport = get_airport("aws", region)
        nl.append(["aws", airport, node, status, size, country, region, zone, public_ip, private_ip])

    return(nl)


def eqn_node_list(conn, region, project):
    nodes = conn.list_nodes(project)

    nl = []
    for n in nodes:
        node = n.name
        public_ip = n.public_ips[0]
        private_ip = n.private_ips[0]
        size = str(n.size.id)
        country = str(n.extra["facility"]["metro"]["country"]).lower()
        region = f"{n.extra['facility']['metro']['name']}"
        airport = get_airport("eqn", region)
        location = n.extra["facility"]["code"]
        status = n.state
        nl.append(["eqn", airport, node, status, size, country, region, location, public_ip, private_ip])

    return(nl)


def list_providers():
    """List supported cloud providers."""

    p = PrettyTable()
    p.field_names = ["Provider", "Libcloud Name", "Description"]
    p.add_rows(PROVIDERS)
    p.align["Libcloud Name"] = "l"
    p.align["Description"] = "l"
    print(p)

    return


def list_airports(geo=None, country=None, airport=None, provider=None):
   """List airport codes & provider regions."""

   al = airport_list(geo, country, airport, provider)
   p = PrettyTable()
   p.field_names = ["Geo", "Country", "Airport", "Area", "Lattitude", "Longitude", "Provider", "Region", "Parent", "Zones"]
   p.float_format = ".4"
   p.align["Lattitude"] = "r"
   p.align["Longitude"] = "r"
   p.align["Area"] = "l"
   p.align["Region"] = "l"
   p.align["Parent"] = "l"
   p.align["Zones"] = "l"
   p.add_rows(al)
   print(p)

def load_config(section):
    # make section an alias
    if section == "equinixmetal":
        section = "eqn"
    elif section == "ec2":
        section = "aws"

    if not os.path.exists(CONFIG):
        util.exit_message(f"config file {CONFIG} missing")
    try:
        config = configparser.ConfigParser()
        rc = config.read(CONFIG)
        sect = config[section]
        return(sect)
    except Exception:
        util.exit_message(f"missing section '{section}' in config file '{CONFIG}'")

    return None


def get_connection(provider=None, region=None, project=None):
    sect = load_config(provider)

    # convert provider to libcloud from an alias
    if provider == "aws":
        provider = "ec2"
    elif provider == "eqn":
        provider = "equinixmetal"
    elif provider == "akm":
        provider = "linode"

    try:
        Driver = libcloud.compute.providers.get_driver(provider)
        if provider in ("equinixmetal"):
            p1 = sect["api_token"]
            conn = Driver(p1)
            if not project:
                project = sect["project"]
        elif provider in ("ec2"):
            p1 = sect["access_key_id"]
            p2 = sect["secret_access_key"]
            if not region:
                region = sect["region"]
            conn = Driver(p1, p2, region=region )
        elif provider in ("linode"):
            p1 = sect["access_token"]
            conn = Driver(p1)
        else:
            util.exit_message(f"Invalid provider '{provider}'")
    except Exception as e:
        util.exit_message(str(e), 1)

    airport = get_airport(provider, region)

    return (conn, sect, region, airport, project)



def is_region(region):
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT count(*) FROM airport_regions WHERE region = '{region}'")
        data = cursor.fetchone()
        if data[0] > 0:
            return(True)
    except Exception as e:
        util.exit_message(f"is_region({region}) ERROR:\n {str(e)}", 1)

    return(False)


def is_parent(parent):
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT count(*) FROM airport_regions WHERE parent = '{parent}'")
        data = cursor.fetchone()
        if data[0] > 0:
            return(True)
    except Exception as e:
        util.exit_message(f"is_parent({parent}) ERROR:\n {str(e)}", 1)

    return(False)


def is_airport(airport):
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT count(*) FROM airports WHERE airport = '{airport}'")
        data = cursor.fetchone()
        if data[0] > 0:
            return(True)
    except Exception as e:
        util.exit_message(f"is_airport({airport}) ERROR:\n {str(e)}", 1)

    return(False)


def get_region(provider, airport):
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT region  FROM airport_regions WHERE provider = '{provider}' AND airport = '{airport}'")
        data = cursor.fetchone()
        if data:
            return(str(data[0]))
    except Exception as e:
        util.exit_message(f"get_region({provider}:{airport}) ERROR:\n {str(e)}")

    return(None)


def get_airport(provider, region):
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT airport FROM airport_regions WHERE provider = '{provider}' AND region = '{region}'")
        data = cursor.fetchone()
        if data:
            return(str(data[0]))
    except Exception as e:
        util.exit_message(f"get_airport({provider}:{region}) ERROR:\n {str(e)}", 1)

    return(None)


def airport_list(geo=None, country=None, airport=None, provider=None):
    wr = "1 = 1"
    if geo:
        wr = wr + f" AND geo = '{geo}'"
    if country:
        wr = wr + f" AND country = '{country}'"
    if airport:
        wr = wr + f" AND airport = '{airport}'"
    if provider:
        wr = wr + f" AND provider= '{provider}'"
    cols = "geo, country, airport, airport_area, lattitude, longitude, provider, region, parent, zones"
    try:
        cursor = cL.cursor()
        cursor.execute(f"SELECT {cols} FROM v_airports WHERE {wr}")
        data = cursor.fetchall()
    except Exception as e:
        util.exit_message(str(e), 1)
    al = []
    for d in data:
        al.append([str(d[0]), str(d[1]), str(d[2]), str(d[3]), d[4],
                   d[5], str(d[6]), str(d[7]), str(d[8]), str(d[9])])
    return (al)


def cluster_create(cluster_name, nodes):
    """Create a json config file for a remote cluster."""
    nl = str(nodes).split(",")
    if len(nl) < 1:
        util.exit_message("Must be a comma seperated list of 'provider:airport:node_name' triplets")

    cluster.json_create(cluster_name, "remote")

    util.message(f"cluster_create node list = {nl}", "debug")
    for n in nl:
        ns = n.strip()
        nsl = ns.split(":")
        if len(nsl) != 3:
            util.exit_message(f"cannot parse '{ns}' into provider:airport:node_name")
        provider = nsl[0]
        airport = nsl[1]
        region = get_region(provider, airport)
        if region is None:
            util.exit_message(f"invalid provider:airport combo '{provider}:{airport}'")
        node_name = nsl[2]
        name, public_ip, status, zone, size = get_node_values(provider, region, node_name)

        if name is None:
            util.exit_message(f"node {node_name} not found for {provider}:{airport}")

        sect = load_config(provider)
        ssh_key = sect["ssh_key"]
        os_user = sect["os_user"]

        util.message(f"cluster_create node_values = {name}, {public_ip}, {status}", "debug")

        cluster.json_add_node(cluster_name, "remote", node_name, True, public_ip, 5432, "/opt/pgedge", os_user=os_user, ssh_key=ssh_key, provider=provider, airport=airport)

    return 


# MAINLINE ################################################################
cL = sqlite3.connect(util.MY_LITE, check_same_thread=False)

if __name__ == "__main__":
    fire.Fire(
        {
            "list-providers": list_providers,
            "list-airports":  list_airports,
            "list-sizes":     list_sizes,
            "list-keys":      list_keys,
            "list-nodes":     list_nodes,
            "node-create":    create_node,
            "node-start":     start_node,
            "node-stop":      stop_node,
            "node-reboot":    reboot_node,
            "node-destroy":   destroy_node,
            "cluster-create": cluster_create,
        }
    )
