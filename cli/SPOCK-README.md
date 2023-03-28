# PGEDGE NODECTL SPOCK 
Logical and Multi-Active PostgreSQL node configuration

## Synopsis
    ./nodectl spock <command> [parameters] [options] 

[**install**](doc/spock-install.md)             - Install PG and configure with spock extension<br>
[**validate**](doc/spock-validate.md)           - Check pre-req's for advanced commands<br>
[**tune**](doc/spock-tune.md)                   - Tune for this configuration<br>
[**create-node**](doc/spock-create-node.md)     - Name this spock node<br>
[**create-repset**](doc/spock-create-repset.md) - Define a replication set<br>
[**create-sub**](doc/spock-create-sub.md)       - Create a subscription<br>
[**repset-add-table**](doc/spock-repset-add-table.md)  - Add table(s) to a replication set<br>
[**sub-add-respset**](doc/spock-sub-add-repset.md)     - Add replication set to a subscription<br>
[**show-sub-status**](spock-show-sub-status.md)        - Display the status of the subcription<br>
[**show-sub-table**](doc/spock-show-sub-table.md)      - Display subscription table(s)<br>
[**spock-wait-for-sub-sync**](doc/spock-wait-for-sub-sync.md)  - Pause until subscription is synchronized<br>
[**health-check**](doc/spock-health-check.md)          - Check if PG is accepting connections<br>
[**metrics-check**](doc/spock-metrics-check.md)        - Retrieve advanced DB & OS metrics<br>

## Options
    --json             # Turn on JSON output
    --debug            # Turn on debug logging
    --silent           # Less noisy
    --verbose or -v    # More noisy

