# PGEDGE NODECTL SERVICE CONTROLLER
Service control commands.  Functionality is similar to SYSTEMCTL & BREW SERVICE, except it's cross-platform and works in sandbox mode.

## Synopsis
    ./nodectl service <command> [parameters] [options] 

[**start**](service-start.md)                 - Start server components<br>
[**stop**](doc/service-stop.md)               - Stop server components<br>
[**status**](doc/service-status.md)           - Display status of installed server components<br>
[**reload**](doc/service-reload.md)           - Reload server config files (without a restart)<br>
[**restart**](doc/service-restart.md)         - Stop & then start server components<br>
[**enable**](doc/service-enable.md)           - Enable a server component<br>
[**disable**](doc/service-disable.md)         - Disable component from starting automatically<br>
[**config**](doc/service-config-.md)          - Configure a component<br>
[**init**](doc/service-init.md)               - Initialize a component<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

