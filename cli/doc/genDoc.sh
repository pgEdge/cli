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
$nc spock install           --help
$nc spock validate          --help
$nc spock tune              --help
$nc spock create-node       --help
$nc spock create-repset     --help
$nc spock create-sub        --help
$nc spock repset-add-table  --help
$nc spock sub-add-repset    --help
$nc spock show-sub-status   --help
$nc spock show-sub-table    --help
$nc spock wait-for-sub-sync --help
$nc spock health-check      --help
$nc spock metrics-check     --help

$nc cluster --help
$nc cluster create-local    --help
$nc cluster destroy         --help
$nc cluster validate        --help
$nc cluster init            --help
$nc cluster command         --help
$nc cluster diff-tables     --help

unset pgeMdDir
