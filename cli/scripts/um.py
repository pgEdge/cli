import os
import fire


def run_cmd(p_cmd, p_comp=None):
    nc_cmd = "./ctl " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def list():
    """Display available/installed components"""

    run_cmd("list")


def update():
    """Update with a new list of available components"""

    run_cmd("update")


def install(component):
    """Install a component"""

    run_cmd("install", component)


def remove(component):
    """Uninstall a component"""

    run_cmd("remove", component)


def upgrade(component):
    """Perform an upgrade  to a newer version of a component"""

    run_cmd("upgrade", component)


def downgrade(component):
    """Perform a downgrade to an older version of a component"""

    run_cmd("downgrade", component)


def clean():
    """Delete downloaded component files from local cache"""

    run_cmd("clean")


if __name__ == "__main__":
    fire.Fire(
        {
            "list": list,
            "update": update,
            "install": install,
            "remove": remove,
            "upgrade": upgrade,
            "clean": clean,
        }
    )
