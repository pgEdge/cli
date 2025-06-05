# pgEdge CLI
This is the pgEdge Command Line Interface (CLI).  It is a cross-platform 
tool to manage your PostgreSQL eco-system of components.  The modules are 
SPOCK, ACE, DB, CLUSTER, VM, LOCALHOST, UM & SERVICE.

## Synopsis
    ./pgedge <command> [parameters] [options] <flags> 
    ./pgedge <module> <command> [parameters] [options] <flags> 

## Commands

setup - Install a pgEdge node (including PostgreSQL, spock, and snowflake-sequences)

upgrade-cli - Upgrade pgEdge CLI to latest stable version

## Modules

spock - Logical and multi-Active PostgreSQL node configuration

ace - The Active Consistency Engine to help prove your active-active nodes are in sync.

db - Configure and control PostgreSQL Databases

cluster - Create and control clusters 

localhost - Easily configure localhost test clusters

um - Update Manager commands

service - Service control commands

## FLAGS

--pg NN: If multiple versions of PostgreSQL are installed due to a migration, this flag will allow you to use the CLI against the intended version. 

--debug
--verbose
--json

