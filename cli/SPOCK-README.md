# PGEDGE NODECTL SPOCK 
Logical and Multi-Master PostgreSQL node configuration

## Synopsis
    ./nodectl spock <command> [parameters] [options] 

[**node-create**](doc/spock-node-create.md)     - Name this spock node<br>
[**node-drop**](doc/spock-node-drop.md)         - Drop this spock node from the cluster<br>
[**repset-create**](doc/spock-repset-create.md) - Define a replication set<br>
[**repset-drop**](doc/spock-repset-drop.md) - Drop a replication set<br>
[**repset-add-table**](doc/spock-repset-add-table.md)  - Add table(s) to a replication set<br>
[**repset-remove-table**](doc/spock-repset-remove-table.md)  - remove table(s) from a replication set<br>
[**repset-list-tables**](doc/spock-repset-list-tables.md)  - List the tables in a replication set<br>
[**sub-create**](doc/spock-sub-create.md)       - Create a subscription<br>
[**sub-enable**](doc/spock-sub-enable.md)       - Enable a subscription<br>
[**sub-disable**](doc/spock-sub-disable.md)       - Disable a subscription<br>
[**sub-drop**](doc/spock-sub-drop.md)       - Remove a subscription<br>
[**sub-add-repset**](doc/spock-sub-add-repset.md)     - Add replication set to a subscription<br>
[**sub-show-status**](doc/spock-sub-show-status.md)        - Display the status of the subcription<br>
[**sub-show-table**](doc/spock-sub-show-table.md)      - Display subscription table(s)<br>
[**spock-sub-wait-for-sync**](doc/spock-sub-wait-for-sync.md)  - Pause until subscription is synchronized<br>
[**health-check**](doc/spock-health-check.md)          - Check if PG is accepting connections<br>
[**metrics-check**](doc/spock-metrics-check.md)        - Retrieve advanced DB & OS metrics<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

