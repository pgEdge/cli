# pgedge/nodectl - Release Notes


## done so far for 23.117 by 2023-06-05:
  - these release notes
  - add support for hypopg-pg15 & -pg16
  - add support for timescaledb-pg15
  - add support for postgis-pg15
  - fix several error message typos (thank u Susan)
  - switch from using JDK11 to JDK17/apache-maven-3.9.2


## scheduled for 23.117 by ~2023-06-12
  - add support for pljava-pg15 & -pg16 (cannot find libjvm17  setting from util.get_jvm_location)
  - get latest pgcat2 & postgrest and make work for arm9 and el9
  - make `cluster create-local` use passwordless ssh on localhost
  - make `cluster create-remote` work with same logic as `create-local`

## done for 23.116 on 2023-05-20
  - `cluster create-local`
  - add support for pg16 beta1

## done for 23.115 on 2023-05-01
  - add support for







