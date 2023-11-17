import sys, os
import fire


def run_cmd(p_cmd, p_comp):
    nc_cmd = "./nodectl " + p_cmd
    if p_comp:
        nc_cmd = nc_cmd + " " + p_comp
    rc = os.system(nc_cmd)
    return rc


def start(component=None):
    """Start server components"""

    run_cmd("start", component)


def stop(component=None):
    """Stop server components"""

    run_cmd("stop", component)


def status(component=None):
    """Display running status of installed server components"""

    run_cmd("status", component)


def restart(component):
    """Stop & then start server components"""

    run_cmd("restart", component)


def reload(component):
    """Reload server configuration files (without a restart)"""

    run_cmd("reload", component)


def enable(component):
    """Enable a component"""

    run_cmd("enable", component)


def disable(component):
    """Disable a server component from starting automatically"""

    run_cmd("disable", component)


def config(component):
    """Config a component"""

    run_cmd("config", component)


def init(component):
    """Initialize a component"""

    run_cmd("init", component)


if __name__ == "__main__":
    fire.Fire(
        {
            "start": start,
            "stop": stop,
            "status": status,
            "restart": restart,
            "reload": reload,
            "enable": enable,
            "disable": disable,
            "config": config,
            "init": init,
        }
    )
