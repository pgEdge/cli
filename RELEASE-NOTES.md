# pgedge/nodectl - Release Notes

## scheduled for 23.118++
  - add test support for zookeeper & patroni
  - add support for pljava-pg15 & -pg16 (cannot find libjvm17  setting from util.get_jvm_location)
  - get latest pgcat2 & postgrest and make work for arm9 and el9
  - make `cluster create-remote` work with same logic as `create-local`
  - add test support for kafka, & patroni
  - add test support for pgcat & fs (failover-slots)
  - add test support for kafka/confluent


########################################################

## done far for 23.117  2023-06-08:
  - fix broken LLVM support in pg15.3-2 & pg16beta1-2
  - these release notes
  - add support for hypopg-pg15/16
  - add support for timescaledb-pg15
  - add support for postgis-pg15
  - fix several error message typos (thank u Susan)
  - switch from using JDK11 to JDK17
  - wip `cluster create-local` use passwordless ssh on localhost


## done for 23.116 on 2023-05-20
  - `cluster create-local`
  - add support for pg16 beta1







