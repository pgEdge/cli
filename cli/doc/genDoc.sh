export pgeMdDir=$NC/cli/doc
nc=../../out/posix/nc

$nc um --help
$nc um list                 --help
$nc um update               --help
$nc um install              --help
$nc um remove               --help
$nc um upgrade              --help
$nc um clean                --help

$nc service --help
$nc service start           --help
$nc service stop            --help
$nc service status          --help
$nc service reload          --help
$nc service restart         --help
$nc service enable          --help
$nc service disable         --help
$nc service config          --help
$nc service init            --help

$nc spock --help
$nc spock node-create       --help
$nc spock node-drop         --help
$nc spock repset-create     --help
$nc spock repset-drop       --help
$nc spock repset-add-table  --help
$nc spock repset-remove-table --help
$nc spock repset-list-tables  --help
$nc spock sub-create        --help
$nc spock sub-drop          --help
$nc spock sub-enable        --help
$nc spock sub-disable       --help
$nc spock sub-add-repset    --help
$nc spock sub-remove-repset --help
$nc spock sub-show-status   --help
$nc spock sub-show-table    --help
$nc spock sub-wait-for-sync --help
$nc spock health-check      --help
$nc spock metrics-check     --help
$nc spock set-readonly      --help

$nc cluster --help
$nc cluster create-local      --help
$nc cluster destroy-local     --help
$nc cluster init-remote       --help
$nc cluster reset-remote      --help
$nc cluster import-remote-def --help
$nc cluster command           --help

$nc secure --help
$nc secure login              --help
$nc secure list-clusters      --help
$nc secure list-cluster-nodes --help
$nc secure import-cluster     --help
$nc secure get-cluster-id     --help
$nc secure get-node-id        --help
$nc secure push-metrics       --help
$nc secure create-cluster     --help
$nc secure destroy-cluster    --help

$nc ace --help
$nc ace diff-tables         --help
$nc ace diff-schemas        --help
$nc ace diff-spock          --help

unset pgeMdDir
