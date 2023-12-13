import util, fire


def list(zone="external"):
    """List firewalld external zone sources"""
    rc1 = util.echo_cmd(f"sudo firewall-cmd --list-sources --zone={zone}", echo=False)
    rc2 = util.echo_cmd(f"sudo firewall-cmd --list-ports --zone={zone}", echo=False)


def add(sources, ports, zone="external"):
    """Add firewalld configuration for source IP addresses and ports"""
    print(f"{sources} {ports}")
    action("add", sources, ports, zone)


def remove(sources, ports, zone="external"):
    """Remove firewalld configuration for source IP addresses and ports"""
    action("remove", sources, ports, zone)


def action(action, sources, ports, zone):
    sources = str(sources)
    l_srcs = sources.split(" ")

    ports = str(ports)
    l_prts = ports.split(" ")

    for s in l_srcs:
        s = s.strip()
        if s > "":
            util.echo_cmd(
                f"sudo firewall-cmd --{action}-source={s}  --zone={zone}", echo=True
            )

    for p in l_prts:
        p = p.strip()
        if p > "":
            util.echo_cmd(
                f"sudo firewall-cmd --{action}-port={p}/tcp  --zone={zone}", echo=True
            )

    util.echo_cmd(f"sudo firewall-cmd --runtime-to-permanent", echo=True)


if __name__ == "__main__":
    fire.Fire({"list": list, "add": add, "remove": remove})
