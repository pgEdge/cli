sh: -c: line 3: syntax error near unexpected token `('
sh: -c: line 3: `Example: spock replicate-ddl demo_repset "CREATE TABLE public.mytable (a INT PRIMARY KEY, b INT)" demo" >> /home/build/dev/pgedge/cli/help/spock-replicate-ddl.md'

SYNOPSIS
    ./pgedge spock replicate-ddl REPLICATION_SETS SQL_COMMAND DB

DESCRIPTION
    Replicate DDL statement through replication set(s) 

Example: spock replicate-ddl demo_repset "CREATE TABLE public.mytable (a INT PRIMARY KEY, b INT)" demo

POSITIONAL ARGUMENTS
    REPLICATION_SETS
        One or more replication sets to replicate the ddl command to. Example: demo_repset, 'demo_repset,default'
    SQL_COMMAND
        The SQL command to replicate. Use schema and object name. Example: "CREATE TABLE public.mytable (a INT PRIMARY KEY, b INT)"
    DB
        The name of the database. Example: demo
