
DROP VIEW  IF EXISTS v_versions;
DROP VIEW  IF EXISTS v_grp_cats;

DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS releases;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS grp_cats;
DROP TABLE IF EXISTS grps;

CREATE TABLE grps (
  grp        TEXT     NOT NULL PRIMARY KEY,
  sort_order SMALLINT NOT NULL,
  short_desc TEXT     NOT NULL
);
INSERT INTO grps VALUES ('pg',  1, 'PostgreSQL');
INSERT INTO grps VALUES ('pgc', 2, 'Postgres Community');
INSERT INTO grps VALUES ('ods', 3, 'Other Datastores');

CREATE TABLE grp_cats (
  grp_cat    TEXT     NOT NULL PRIMARY KEY,
  sort_order SMALLINT NOT NULL,
  grp        TEXT     NOT NULL,
  web_page   TEXT     NOT NULL,
  page_title TEXT     NOT NULL,
  short_desc TEXT     NOT NULL,
  FOREIGN KEY (grp) REFERENCES grps(grp)
);
INSERT INTO grp_cats VALUES ('pg',    1, 'pg',  'postgres-core',       'Postgres',        'Core PostgreSQL&reg;');
INSERT INTO grp_cats VALUES ('hyper', 1, 'pgc', 'postgres-hyper',      'HyperscalePG',    'HyperscalePG');
INSERT INTO grp_cats VALUES ('fdw',   2, 'pgc', 'postgres-fdws',       'PG FDWs',         'Foreign Data Wrappers');
INSERT INTO grp_cats VALUES ('ext',   3, 'pgc', 'postgres-extensions', 'PG Extensions',   'Postgres Extensions');
INSERT INTO grp_cats VALUES ('app',   4, 'pgc', 'postgres-apps',       'PG Applications', 'Postgres Applications');
INSERT INTO grp_cats VALUES ('dev',   5, 'pgc', 'postgres-devs',       'PG DevOps',       'For DevOps');
INSERT INTO grp_cats VALUES ('sql',   1, 'ods', 'sql-datastores',      'Other RDBMS',     'Other RDBMS');
INSERT INTO grp_cats VALUES ('strm',  2, 'ods', 'change-data-capture', 'Streaming & CDC', 'Streaming & Change Data Capture');
INSERT INTO grp_cats VALUES ('nosql', 3, 'ods', 'purpose-built',       'Purpose-Built',   'Purpose-Built Datastores');

CREATE VIEW v_grp_cats AS
   SELECT g.sort_order as grp_sort, c.sort_order as cat_sort,
          g.grp, g.short_desc as grp_short_desc, c.grp_cat, c.web_page, c.page_title,
          c.short_desc as grp_cat_desc
     FROM grps g, grp_cats c
    WHERE g.grp = c.grp
 ORDER BY 1, 2;


CREATE TABLE projects (
  project   	 TEXT     NOT NULL PRIMARY KEY,
  grp_cat        TEXT     NOT NULL,
  port      	 INTEGER  NOT NULL,
  depends   	 TEXT     NOT NULL,
  start_order    INTEGER  NOT NULL,
  sources_url    TEXT     NOT NULL,
  short_name     TEXT     NOT NULL,
  is_extension   SMALLINT NOT NULL,
  image_file     TEXT     NOT NULL,
  description    TEXT     NOT NULL,
  project_url    TEXT     NOT NULL,
  FOREIGN KEY (grp_cat) REFERENCES grp_cats(grp_cat)
);


CREATE TABLE releases (
  component     TEXT     NOT NULL PRIMARY KEY,
  sort_order    SMALLINT NOT NULL,
  project       TEXT     NOT NULL,
  disp_name     TEXT     NOT NULL,
  doc_url       TEXT     NOT NULL,
  stage         TEXT     NOT NULL,
  description   TEXT     NOT NULL,
  is_open       SMALLINT NOT NULL DEFAULT 1,
  license       TEXT     NOT NULL,
  is_available  TEXT     NOT NULL,
  available_ver TEXT     NOT NULL,
  FOREIGN KEY (project) REFERENCES projects(project)
);


CREATE TABLE versions (
  component     TEXT    NOT NULL,
  version       TEXT    NOT NULL,
  platform      TEXT    NOT NULL,
  is_current    INTEGER NOT NULL,
  release_date  DATE    NOT NULL,
  parent        TEXT    NOT NULL,
  pre_reqs      TEXT    NOT NULL,
  release_notes TEXT    NOT NULL,
  PRIMARY KEY (component, version),
  FOREIGN KEY (component) REFERENCES releases(component)
);


CREATE VIEW v_versions AS
  SELECT c.grp_sort, c.cat_sort, c.grp, c.grp_short_desc, c.grp_cat, 
         c.web_page, c.page_title, c.grp_cat_desc, r.sort_order as rel_sort,
         p.image_file, r.component, r.project, r.stage, r.disp_name as rel_name,
         v.version, p.sources_url, p.project_url, v.platform, 
         v.is_current, v.release_date as rel_date, p.description as proj_desc, 
         r.description as rel_desc, v.pre_reqs, r.license, p.depends, 
         r.is_available, v.release_notes as rel_notes
    FROM v_grp_cats c, projects p, releases r, versions v
   WHERE c.grp_cat = p.grp_cat
     AND p.project = r.project
     AND r.component = v.component;


-- ## HUB ################################
INSERT INTO projects VALUES ('hub', 'app', 0, 'hub', 0, 'https://github.com/oscg-io/io','',0,'','','');
INSERT INTO releases VALUES ('hub', 1, 'hub', '', '', 'hidden', '', 1, '', '', '');
INSERT INTO versions VALUES ('hub', '0.66', '',  1, '20220615', '', '', '');

-- ##
INSERT INTO projects VALUES ('pg', 'pg', 5432, 'hub', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org');

INSERT INTO releases VALUES ('pg11', 4, 'pg', 'PostgreSQL', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/11/release-11.html>2018</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg11', '11.16-1', 'amd', 1, '20220512', '', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg11', '11.15-1', 'amd', 0, '20220210', '', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg11', '11.14-1', 'amd', 0, '20211111', '', 'LIBC-2.17', '');

INSERT INTO releases VALUES ('pg12', 3, 'pg', 'PostgreSQL', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/12/release-12.html>2019</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg12', '12.11-1', 'amd', 1, '20220512', '', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg12', '12.10-1', 'amd', 0, '20220210', '', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg12', '12.9-1',  'amd', 0, '20211111', '', 'LIBC-2.17', '');

INSERT INTO releases VALUES ('pg13', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/13/release-13.html>2020</a></font>', 
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg13', '13.7-1',  'amd', 1, '20220512','', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg13', '13.6-1',  'amd', 0, '20220210','', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg13', '13.5-4',  'amd', 0, '20211203','', 'LIBC-2.17', '');

INSERT INTO releases VALUES ('pg14', 1, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/14/release-14.html>2021</a></font>',
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg14', '14.4-1',  'amd, osx', 1, '20220616','', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg14', '14.3-1',  'amd, osx', 0, '20220512','', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg14', '14.2-1',  'amd', 0, '20220210','', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('pg14', '14.1-1',  'amd', 0, '20211111','', 'LIBC-2.28', '');

INSERT INTO releases VALUES ('pg15', 5, 'pg', '', '', 'test', 
  '<font size=-1 color=red><b>New in <a href=https://sql-info.de/postgresql/postgresql-15/articles-about-new-features-in-postgresql-15.html>2022!</a></b></font>',
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg15', '15beta1-1',  'amd, osx', 1, '20220519','', 'LIBC-2.17', '');

INSERT INTO projects VALUES ('ivory14', 'var', 5432, 'hub', 1, 'https://github.com/ivorysql/ivorysql/tags',
  'IvorySQL', 0, 'highgo.png', 'Postgres w/ mode=oracle', 'https://ivorysql.org');
INSERT INTO releases VALUES ('ivory14', 12, 'ivory14', 'IvorySQL', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('ivory14', '14.3-1',  'amd', 0, '20220523', '', 'LIBC-2.17', '');
INSERT INTO versions VALUES ('ivory14', '14.2-1',  'amd', 0, '20220228', '', 'LIBC-2.17', '');

INSERT INTO projects VALUES ('debezium', 'strm', 8083, '', 3, 'https://debezium.io/releases/1.9/',
  'Debezium', 0, 'debezium.png', 'Heterogeneous CDC', 'https://debezium.io');
INSERT INTO releases VALUES ('debezium', 6, 'debezium', 'Debezium', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('debezium', '1.9.3.Final',   '', 1, '20220602', '', '', '');

INSERT INTO projects VALUES ('olr', 'strm', 8083, '', 3, 'https://github.com/bersler/OpenLogReplicator/releases',
  'OLR', 0, 'olr.png', 'Oracle Binary Log Replicator', 'https://www.bersler.com/openlogreplicator');
INSERT INTO releases VALUES ('olr', 8, 'olr', 'OLR', '', 'test', '', 1, 'GPL', '', '');
INSERT INTO versions VALUES ('olr', '0.9.43',      '', 1, '20220612', '', '', '');
INSERT INTO versions VALUES ('olr', '0.9.42',      '', 0, '20220604', '', '', '');

INSERT INTO projects VALUES ('kafka', 'strm', 9092, '', 2, 'https://kafka.apache.org/downloads',
  'Kafka', 0, 'kafka.png', 'Streaming Platform', 'https://kafka.apache.org');
INSERT INTO releases VALUES ('kafka', 5, 'kafka', 'Apache Kafka', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('kafka', '3.2.0', '', 1, '20220517', '', '', 'https://downloads.apache.org/kafka/3.2.0/RELEASE_NOTES.html');

INSERT INTO projects VALUES ('redis',  'nosql', 6379, 'hub', 2, 'https://github.com/redis/redis/tags',
  'Redis', 0, 'redis.png', 'In-Memory DataStore', 'https://redis.io');
INSERT INTO releases VALUES ('redis', 7, 'redis', 'Redis 6.2.7', '', 'test', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('redis', '6.2', '', 1, '20220422', '', '', '');

INSERT INTO projects VALUES ('memcached',  'nosql', 6379, 'hub', 2, 'http://memcached.org/downloads',
  'Memcached', 0, 'memcached.png', 'In-Memory Cache', 'http://memcached.org');
INSERT INTO releases VALUES ('memcached', 8, 'memcached', 'Memcached 1.6.15', '', 'test', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('memcached', '1.6', '', 0, '20220329', '', '', '');

INSERT INTO projects VALUES ('mariadb',  'sql', 3306, 'hub', 2, 'https://github.com/mariadb/server/tags',
  'MariaDB', 0, 'mariadb.png', 'Replacement for MySQL', 'https://mariadb.com');
INSERT INTO releases VALUES ('mariadb', 3, 'mariadb', 'MariaDB 10.9.1', '', 'test', '', 1, 'GPL', '', '');
INSERT INTO versions VALUES ('mariadb', '10.9', '',   1, '20220520', '', '', '');

INSERT INTO projects VALUES ('sqlsvr',  'sql', 1433, 'hub', 2, 
  'https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-release-notes-2019?view=sql-server-ver15#release-history',
  'MS SQL Server', 0, 'sqlsvr.png', 'SQL Server for Linux',
  'https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-overview?view=sql-server-ver15');
INSERT INTO releases VALUES ('sqlsvr', 2, 'sqlsvr', 'SQL Server 2019', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('sqlsvr', '15.0.4236', '',   1, '20220614', '', 'UBU20', '');

INSERT INTO projects VALUES ('mongodb',  'nosql', 27017, 'hub', 2, 
  'https://docs.mongodb.com/v5.0/release-notes/5.0/',
  'MongoDB', 0, 'mongodb.png', 'Document Database',
  'https://docs.mongodb.com/v5.0/release-notes/5.0/');
INSERT INTO releases VALUES ('mongodb', 9, 'mongodb', 'MongoDB 5.0', '', 'test', '', 1, 'SSPL', '', '');
INSERT INTO versions VALUES ('mongodb', '5.0.8', '',   1, '20220425', '', '', '');

INSERT INTO projects VALUES ('elasticsearch',  'nosql', 9200, 'hub', 2, 
  'https://www.elastic.co/guide/en/elasticsearch/reference/7.17/es-release-notes.html',
  'Elasticsearch', 0, 'elasticsearch.png', 'Search and Analytics Engine',
  'https://www.elastic.co/elasticsearch/');
INSERT INTO releases VALUES ('elasticsearch', 9, 'elasticsearch', 'Elastic Search 7.17.4', '', 'test', '', 1, 'SSPL', '', '');
INSERT INTO versions VALUES ('elasticsearch', '7.x', '',   1, '20220524', '', 'UBU20', '');

INSERT INTO projects VALUES ('apicurio', 'strm', 8080, 'hub', 1, 'https://github.com/apicurio/apicurio-registry/releases',
  'apicurio', 0, 'apicurio.png', 'Schema Registry', 'https://www.apicur.io/registry/');
INSERT INTO releases VALUES ('apicurio', 6, 'apicurio', 'Apicurio', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.4', '',  1, '20220602', '', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.3', '',  0, '20220414', '', '', '');

INSERT INTO projects VALUES ('zookeeper', 'nosql', 2181, 'hub', 1, 'https://zookeeper.apache.org/releases.html#releasenotes',
  'zookeeper', 0, 'zookeeper.png', 'Distributed Key-Store for HA', 'https://zookeeper.apache.org');
INSERT INTO releases VALUES ('zookeeper', 10, 'zookeeper', 'Zookeeper', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('zookeeper', '3.8.0', '',  1, '20220307', '', '',
  'https://zookeeper.apache.org/doc/r3.8.0/releasenotes.html');

INSERT INTO projects VALUES ('cassandrafdw', 'fdw', 0, 'hub', 0, 'https://github.com/pgsql-io/cassandra_fdw/releases', 
  'cstarfdw', 1, 'cstar.png', 'Cassandra from PG', 'https://github.com/pgsql-io/cassandra_fdw#cassandra_fdw');
INSERT INTO releases VALUES ('cassandrafdw-pg12', 12, 'cassandrafdw', 'CassandraFDW','','test', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('cassandrafdw-pg12', '3.1.5-1', 'amd', 0, '20191230', 'pg12', '', '');

INSERT INTO projects VALUES ('decoderbufs', 'strm', 0, 'hub', 0, 'https://github.com/debezium/postgres-decoderbufs', 
  'decoderbufs', 1, 'protobuf.png', 'Logical decoding via ProtoBuf', 'https://github.com/debezium/postgres-decoderbufs');
INSERT INTO releases VALUES ('decoderbufs-pg13',  8, 'decoderbufs', 'DecoderBufs', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO releases VALUES ('decoderbufs-pg14',  8, 'decoderbufs', 'DecoderBufs', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('decoderbufs-pg13', '1.7.0-1', 'amd', 0, '20211001', 'pg13', '', '');
INSERT INTO versions VALUES ('decoderbufs-pg14', '1.7.0-1', 'amd', 0, '20211001', 'pg14', '', '');

INSERT INTO projects VALUES ('wal2json', 'ext', 0, 'hub', 0, 'https://github.com/eulerto/wal2json/tags', 
  'wal2json', 1, 'wal2json.png', 'Logical decoding via JSON ', 'https://github.com/eulerto/wal2json#introduction');
INSERT INTO releases VALUES ('wal2json-pg13',  3, 'wal2json', 'wal2json', '', 'prod', '', 1, 'BSD', '', '');
INSERT INTO releases VALUES ('wal2json-pg14',  3, 'wal2json', 'wal2json', '', 'prod', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('wal2json-pg13', '2.4-1', 'amd', 0, '20210831', 'pg13', '', '');
INSERT INTO versions VALUES ('wal2json-pg14', '2.4-1', 'amd', 0, '20210831', 'pg14', '', '');

INSERT INTO projects VALUES ('mongofdw', 'fdw', 0, 'hub', 0, 'https://github.com/EnterpriseDB/mongo_fdw/tags', 
  'mongofdw', 1, 'mongodb.png', 'MongoDB from PG', 'https://github.com/EnterpriseDB/mongo_fdw#mongo_fdw');
INSERT INTO releases VALUES ('mongofdw-pg13',  3, 'mongofdw', 'MongoFDW', '', 'prod', '', 1, 'AGPLv3', '', '');
INSERT INTO releases VALUES ('mongofdw-pg14',  3, 'mongofdw', 'MongoFDW', '', 'prod', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('mongofdw-pg13', '5.3.0-1', 'amd', 0, '20211117', 'pg13', '', '');
INSERT INTO versions VALUES ('mongofdw-pg14', '5.4.0-1', 'amd', 1, '20220519', 'pg14', '', '');
INSERT INTO versions VALUES ('mongofdw-pg14', '5.3.0-1', 'amd', 0, '20211117', 'pg14', '', '');

INSERT INTO projects VALUES ('hivefdw', 'fdw', 0, 'hub', 0, 'https://github.com/pgsql-io/hive_fdw/tags', 
  'hivefdw', 1, 'hive.png', 'Big Data Queries from PG', 'https://github.com/pgsql-io/hive_fdw#hive_fdw');
INSERT INTO releases VALUES ('hivefdw-pg13', 14, 'hivefdw', 'HiveFDW', '', 'test', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('hivefdw-pg13', '4.0-1', 'amd', 0, '20200927', 'pg13', '', '');

INSERT INTO projects VALUES ('pgredis', 'fdw', 0, 'hub', 0, 'https://github.com/pgsql-io/pg_redis/tags', 
  'pgredis', 1, 'redis.png', 'Leverage Redis as a Hi-speed cache', 'https://github.com/pgsql-io/pg_redis');
INSERT INTO releases VALUES ('pgredis-pg14',  2, 'pgredis', 'PgRedis',  '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pgredis-pg14', '2.0-1', 'amd', 0, '20210620', 'pg14', '', '');

INSERT INTO projects VALUES ('mysqlfdw', 'fdw', 0, 'hub', 0, 'https://github.com/EnterpriseDB/mysql_fdw/tags', 
  'mysqlfdw', 1, 'mysql.png', 'MySQL & MariaDB from PG', 'https://github.com/EnterpriseDb/mysql_fdw');
INSERT INTO releases VALUES ('mysqlfdw-pg14',  4, 'mysqlfdw', 'MySQL FDW',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('mysqlfdw-pg13',  4, 'mysqlfdw', 'MySQL FDW',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('mysqlfdw-pg13', '2.7.0-1', 'amd', 0, '20211117', 'pg13', '', '');
INSERT INTO versions VALUES ('mysqlfdw-pg14', '2.7.0-1', 'amd', 1, '20211117', 'pg14', '', '');

INSERT INTO projects VALUES ('tdsfdw', 'fdw', 0, 'hub', 0, 'https://github.com/tds-fdw/tds_fdw/tags',
  'tdsfdw', 1, 'tds.png', 'SQL Svr & Sybase from PG', 'https://github.com/tds-fdw/tds_fdw/#tds-foreign-data-wrapper');
INSERT INTO releases VALUES ('tdsfdw-pg13', 4, 'tdsfdw', 'TDS FDW', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('tdsfdw-pg13', '2.0.2-1', 'amd', 1, '20200926', 'pg13', '', 'https://github.com/tds-fdw/tds_fdw/releases/tag/v2.0.2');

INSERT INTO projects VALUES ('proctab', 'ext', 0, 'hub', 0, 'https://github.com/markwkm/pg_proctab/releases',
  'proctab', 1, 'proctab.png', 'Monitoring Functions for pgTop', 'https://github.com/markwkm/pg_proctab');
INSERT INTO releases VALUES ('proctab-pg12', 8, 'proctab', 'pgProcTab', '', 'prod', '', 1, 'BSD-3', '', '');
INSERT INTO versions VALUES ('proctab-pg12', '0.0.9-1', 'amd',  0, '20200508', 'pg12', '', '');

INSERT INTO projects VALUES ('pgtop', 'ext', 0, 'proctab', 0, 'https://github.com/markwkm/pg_top/releases',
  'pgtop', 1, 'pgtop.png', '"top" for Postgres', 'https://github.com/markwkm/pg_top/');
INSERT INTO releases VALUES ('pgtop-pg12', 8, 'pgtop', 'pgTop', '', 'prod', '', 1, 'BSD-3', '', '');
INSERT INTO versions VALUES ('pgtop-pg12', '4.0.0-1', 'amd',  0, '20201008', 'pg12', '', '');

INSERT INTO projects VALUES ('bqfdw', 'fdw', 0, 'multicorn2', 1, 'https://pypi.org/project/bigquery-fdw/#history',
  'bqfdw', 1, 'bigquery.png', 'BigQuery from PG', 'https://pypi.org/project/bigquery-fdw');
INSERT INTO releases VALUES ('bqfdw-pg13',  3, 'bqfdw', 'BigQueryFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO releases VALUES ('bqfdw-pg14',  3, 'bqfdw', 'BigQueryFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('bqfdw-pg13', '1.9', 'amd',  0, '20211218', 'pg13', '', '');
INSERT INTO versions VALUES ('bqfdw-pg14', '1.9', 'amd',  1, '20211218', 'pg14', '', '');

INSERT INTO projects VALUES ('esfdw', 'fdw', 0, 'multicorn2', 1, 'https://pypi.org/project/pg-es-fdw/#history',
  'esfdw', 1, 'esfdw.png', 'ElasticSearch from PG', 'https://pypi.org/project/pg-es-fdw/');
INSERT INTO releases VALUES ('esfdw-pg13',  4, 'esfdw', 'ElasticSearchFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO releases VALUES ('esfdw-pg14',  4, 'esfdw', 'ElasticSearchFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('esfdw-pg13', '0.11.1', 'amd',  0, '20210409', 'pg13', '', '');
INSERT INTO versions VALUES ('esfdw-pg14', '0.11.1', 'amd',  1, '20210409', 'pg14', '', '');

INSERT INTO projects VALUES ('ora2pg', 'app', 0, 'hub', 0, 'https://github.com/darold/ora2pg/tags',
  'ora2pg', 0, 'ora2pg.png', 'Migrate from Oracle to PG', 'https://ora2pg.darold.net');
INSERT INTO releases VALUES ('ora2pg', 2, 'ora2pg', 'Oracle to PG', '', 'test', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('ora2pg', '23.1', '', 1, '20220512', '', '', 'https://github.com/darold/ora2pg/releases/tag/v23.1');

INSERT INTO projects VALUES ('oraclefdw', 'fdw', 0, 'hub', 0, 'https://github.com/laurenz/oracle_fdw/tags',
  'oraclefdw', 1, 'oracle_fdw.png', 'Oracle from PG', 'https://github.com/laurenz/oracle_fdw');
INSERT INTO releases VALUES ('oraclefdw-pg13', 2, 'oraclefdw', 'OracleFDW', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('oraclefdw-pg14', 2, 'oraclefdw', 'OracleFDW', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('oraclefdw-pg13','2.4.0-1', 'amd', 0, '20210923', 'pg13', '', 'https://github.com/laurenz/oracle_fdw/releases/tag/ORACLE_FDW_2_4_0');
INSERT INTO versions VALUES ('oraclefdw-pg14','2.4.0-1', 'amd', 1, '20210923', 'pg14', '', 'https://github.com/laurenz/oracle_fdw/releases/tag/ORACLE_FDW_2_4_0');

INSERT INTO projects VALUES ('oracle',  'sql', 1521, 'hub', 0, 'https://www.oracle.com/database/technologies/oracle-database-software-downloads.html#19c', 
  'oracle', 0, 'oracle.png', 'Oracle Express for Linux', 'https://www.oracle.com/database/technologies');
INSERT INTO releases VALUES ('oracle', 1, 'oracle', 'Oracle', '', 'test','', 0, 'ORACLE', '', '');
INSERT INTO versions VALUES ('oracle', '11', 'amd', 1, '20180501', '', '', '');

INSERT INTO projects VALUES ('instantclient', 'sql', 0, 'hub', 0, 'https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html', 
  'instantclient', 0, 'instantclient.png', 'Oracle Instant Client', 'https://www.oracle.com/database/technologies/instant-client.html');
INSERT INTO releases VALUES ('instantclient', 2, 'instantclient', 'Instant Client', '', 'test','', 0, 'ORACLE', '', '');
INSERT INTO versions VALUES ('instantclient', '21.6', '', 0, '20220420', '', '', '');

INSERT INTO projects VALUES ('plusql', 'app', 1, 'hub', 0, 'https://github.com/pgsql-io/plusql2/tags',
  'plusql', 0, 'plusql.png', 'SQL*PLUS<sup>&reg;</sup> Compatible CLI', 'https://github.com/pgsql-io/plusql2');
INSERT INTO releases VALUES ('plusql', 99, 'plusql', 'PlusQL', '', 'test', '', 0, 'SSPL', '', '');
INSERT INTO versions VALUES ('plusql', '0.2',  'amd', 0, '20210908', '', '', '');

INSERT INTO projects VALUES ('orafce', 'ext', 0, 'hub', 0, 'https://github.com/orafce/orafce/releases',
  'orafce', 1, 'larry.png', 'Ora Built-in Packages', 'https://github.com/orafce/orafce#orafce---oracles-compatibility-functions-and-packages');
INSERT INTO releases VALUES ('orafce-pg13', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('orafce-pg14', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('orafce-pg13', '3.18.1-1',  'amd', 0, '20220114', 'pg13', '', '');
INSERT INTO versions VALUES ('orafce-pg14', '3.21.0-1',  'amd', 1, '20220416', 'pg14', '', '');
INSERT INTO versions VALUES ('orafce-pg14', '3.18.1-1',  'amd', 0, '20220114', 'pg14', '', '');

INSERT INTO projects VALUES ('fixeddecimal', 'ext', 0, 'hub', 0, 'https://github.com/pgsql-io/fixeddecimal/tags',
  'fixeddecimal', 1, 'fixeddecimal.png', 'Much faster than NUMERIC', 'https://github.com/pgsql-io/fixeddecimal');
INSERT INTO releases VALUES ('fixeddecimal-pg13', 90, 'fixeddecimal', 'FixedDecimal', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('fixeddecimal-pg14', 90, 'fixeddecimal', 'FixedDecimal', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('fixeddecimal-pg13', '1.1.0-1',  'amd', 0, '20201119', 'pg13', '', '');
INSERT INTO versions VALUES ('fixeddecimal-pg14', '1.1.0-1',  'amd', 0, '20201119', 'pg14', '', '');

INSERT INTO projects VALUES ('plr', 'dev', 0, 'hub', 0, 'https://github.com/postgres-plr/plr/releases',
  'plr',   1, 'r-project.png', 'R Stored Procedures', 'https://github.com/postgres-plr/plr');
INSERT INTO releases VALUES ('plr-pg12', 4, 'plr', 'PL/R 8.4.1', '', 'soon', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plr-pg12', '8.4-1', 'amd', 0, '20200912', 'pg12', '', '');

INSERT INTO projects VALUES ('plv8', 'hyper', 0, 'hub', 0, 'https://github.com/plv8/plv8/tags',
  'plv8',   1, 'v8.png', 'Javascript Stored Procedures', 'https://github.com/plv8/plv8');
INSERT INTO releases VALUES ('plv8-pg12', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plv8-pg13', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plv8-pg14', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plv8-pg12', '2.3.15-1', 'amd', 0, '20200711', 'pg12', '', '');
INSERT INTO versions VALUES ('plv8-pg13', '2.3.15-1', 'amd', 0, '20200711', 'pg13', '', '');
INSERT INTO versions VALUES ('plv8-pg14', '2.3.15-1', 'amd', 1, '20200711', 'pg14', '', '');

INSERT INTO projects VALUES ('plpython', 'dev', 0, 'hub', 0, 'https://www.postgresql.org/docs/13/plpython.html',
  'plpython', 1, 'python.png', 'Python3 Stored Procedures', 'https://www.postgresql.org/docs/13/plpython.html');
INSERT INTO releases VALUES ('plpython3', 5, 'plpython', 'PL/Python','', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plpython3', '13', 'amd', 0, '20200213', 'pg13', '', '');

INSERT INTO projects VALUES ('plperl', 'dev', 0, 'hub', 0, 'https://www.postgresql.org/docs/13/plperl.html',
	'plperl', 1, 'perl.png', 'Perl Stored Procedures', 'https://www.postgresql.org/docs/13/plperl.html');
INSERT INTO releases VALUES ('plperl', 6, 'plperl', 'PL/Perl','', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plperl', '13', 'amd', 0, '20200213', 'pg13', '', '');

INSERT INTO projects VALUES ('pljava', 'dev', 0, 'hub', 0, 'https://github.com/tada/pljava/releases', 
  'pljava', 1, 'pljava.png', 'Java Stored Procedures', 'https://github.com/tada/pljava');
INSERT INTO releases VALUES ('pljava-pg13', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pljava-pg13', '1.6.2-1',  'amd',  0, '20201127', 'pg13', '', '');

INSERT INTO projects VALUES ('pldebugger', 'dev', 0, 'hub', 0, 'https://github.com/EnterpriseDB/pldebugger/tags',
  'pldebugger', 1, 'debugger.png', 'Stored Procedure Debugger', 'https://github.com/EnterpriseDB/pldebugger');
INSERT INTO releases VALUES ('pldebugger-pg12', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pldebugger-pg13', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pldebugger-pg14', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pldebugger-pg12', '1.4-1',  'amd',  0, '20210923', 'pg12', '', '');
INSERT INTO versions VALUES ('pldebugger-pg13', '1.4-1',  'amd',  0, '20210923', 'pg13', '', '');
INSERT INTO versions VALUES ('pldebugger-pg14', '1.4-1',  'amd',  1, '20210923', 'pg14', '', '');

INSERT INTO projects VALUES ('plpgsql', 'dev', 0, 'hub', 0, 'https://www.postgresql.org/docs/13/plpgsql-overview.html',
  'plpgsql', 0, 'jan.png', 'Postgres Procedural Language', 'https://www.postgresql.org/docs/13/plpgsql-overview.html');
INSERT INTO releases VALUES ('plpgsql', 1, 'plpgsql', 'PL/pgSQL', '', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plpgsql', '14',  'amd',  0, '20210930', '', '', '');

INSERT INTO projects VALUES ('pgtsql', 'dev', 0, 'hub', 0, 'https://github.com/bigsql/pgtsql/releases',
  'pgtsql', 1, 'tds.png', 'Transact-SQL Procedures', 'https://github.com/bigsql/pgtsql#pgtsql');
INSERT INTO releases VALUES ('pgtsql-pg13', 3, 'pgtsql', 'PL/pgTSQL','', 'soon', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('pgtsql-pg13', '3.0-1', 'amd', 0, '20191119', 'pg13', '', '');

INSERT INTO projects VALUES ('plprofiler', 'dev', 0, 'hub', 7, 'https://github.com/bigsql/plprofiler/tags',
  'plprofiler', 1, 'plprofiler.png', 'Stored Procedure Profiler', 'https://github.com/bigsql/plprofiler#plprofiler');
INSERT INTO releases VALUES ('plprofiler-pg12', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg13', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg14', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plprofiler-pg12', '4.1-1', 'amd', 0, '20211019', 'pg12', '', '');
INSERT INTO versions VALUES ('plprofiler-pg13', '4.1-1', 'amd', 0, '20211019', 'pg13', '', '');
INSERT INTO versions VALUES ('plprofiler-pg14', '4.1-1', 'amd', 1, '20211019', 'pg14', '', '');

INSERT INTO projects VALUES ('golang', 'dev', 0, 'hub', 0, 'https://go.dev/dl',
  'golang', 0, 'go.png', 'Fast & Scaleable Programming', 'https://go.dev');
INSERT INTO releases VALUES ('golang', 9, 'golang', 'GO', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('golang', '1.17.4', 'amd', 0, '20210812', '', '', '');

INSERT INTO projects VALUES ('walg', 'hyper', 0, 'hub', 0, 'https://github.com/wal-g/wal-g/releases',
  'walg', 0, 'walg.png', 'Archival Restoration Tool', 'https://wal-g.readthedocs.io');
INSERT INTO releases VALUES ('walg', 9, 'walg', 'WAL-G', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('walg', '2.0.0', 'amd', 1, '20220519', '', '', '');

INSERT INTO projects VALUES ('backrest', 'app', 0, 'hub', 0, 'https://github.com/pgbackrest/pgbackrest/tags',
  'backrest', 0, 'backrest.png', 'Backup & Restore', 'https://pgbackrest.org');
INSERT INTO releases VALUES ('backrest', 9, 'backrest', 'pgBackRest', '', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('backrest', '2.38', 'amd', 0, '20220307', '', '', 'https://pgbackrest.org/release.html#2.38');

INSERT INTO projects VALUES ('audit', 'hyper', 0, 'hub', 0, 'https://github.com/pgaudit/pgaudit/releases',
  'audit', 1, 'audit.png', 'Audit Logging', 'https://github.com/pgaudit/pgaudit');
INSERT INTO releases VALUES ('audit-pg14', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('audit-pg14', '1.6.2-1', 'amd', 1, '20220225', 'pg14', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.6.2');
INSERT INTO versions VALUES ('audit-pg14', '1.6.1-1', 'amd', 0, '20211104', 'pg14', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.6.1');

INSERT INTO projects VALUES ('hintplan', 'ext', 0, 'hub', 0, 'https://github.com/ossc-db/pg_hint_plan/tags',
  'hintplan', 1, 'hintplan.png', 'Execution Plan Hints', 'https://github.com/ossc-db/pg_hint_plan');
INSERT INTO releases VALUES ('hintplan-pg14', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hintplan-pg14', '1.4.0-1', 'amd', 1, '20220118', 'pg14', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.6.0');

INSERT INTO projects VALUES ('anon', 'ext', 0, 'ddlx', 1, 'https://gitlab.com/dalibo/postgresql_anonymizer/-/tags',
  'anon', 1, 'anon.png', 'Anonymization & Masking', 'https://gitlab.com/dalibo/postgresql_anonymizer/blob/master/README.md');
INSERT INTO releases VALUES ('anon-pg13', 11, 'anon', 'Anonymizer', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('anon-pg14', 11, 'anon', 'Anonymizer', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('anon-pg13', '0.9.0-1', 'amd', 0, '20210703', 'pg13', '', '');

INSERT INTO versions VALUES ('anon-pg14', '0.12.0-1', 'amd', 1, '20220413', 'pg14', '', '');
INSERT INTO versions VALUES ('anon-pg14', '0.10.0-1', 'amd', 0, '20220315', 'pg14', '', '');
INSERT INTO versions VALUES ('anon-pg14', '0.9.0-1', 'amd', 0, '20210703', 'pg14', '', '');

INSERT INTO projects VALUES ('citus', 'hyper', 0, 'hub',0, 'https://github.com/citusdata/citus/releases',
  'citus', 1, 'citus.png', 'Distributed PostgreSQL', 'https://github.com/citusdata/citus');
INSERT INTO releases VALUES ('citus-pg13',  0, 'citus', 'Citus', '', 'prod', '', 1, 'AGPLv3', '', '');
INSERT INTO releases VALUES ('citus-pg14',  0, 'citus', 'Citus', '', 'test', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('citus-pg14', '11.0.2', 'amd', 1, '20220616', 'pg14', '', 'https://github.com/citusdata/citus/releases/tag/v11.0.1_beta');

INSERT INTO projects VALUES ('cron', 'hyper', 0, 'hub',0, 'https://github.com/citusdata/pg_cron/releases',
  'cron', 1, 'cron.png', 'Background Job Scheduler', 'https://github.com/citusdata/pg_cron');
INSERT INTO releases VALUES ('cron-pg13', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('cron-pg14', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('cron-pg13', '1.4.1-1', 'amd', 0, '20210925', 'pg13', '', '');
INSERT INTO versions VALUES ('cron-pg14', '1.4.1-1', 'amd', 1, '20210925', 'pg14', '', '');

INSERT INTO projects VALUES ('timescaledb', 'ext', 0, 'hub', 1, 'https://github.com/timescale/timescaledb/releases',
   'timescaledb', 1, 'timescaledb.png', 'Time Series Data', 'https://github.com/timescale/timescaledb/#timescaledb');
INSERT INTO releases VALUES ('timescaledb-pg12',  0, 'timescaledb', 'TimescaleDB', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO releases VALUES ('timescaledb-pg13',  0, 'timescaledb', 'TimescaleDB', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO releases VALUES ('timescaledb-pg14',  0, 'timescaledb', 'TimescaleDB', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('timescaledb-pg13', '2.5.2-1',  'amd', 0, '20220209', 'pg13', '', 'https://github.com/timescale/timescaledb/releases/tag/2.5.2');
INSERT INTO versions VALUES ('timescaledb-pg14', '2.7.0-1',  'amd', 1, '20220524', 'pg14', '', 'https://github.com/timescale/timescaledb/releases/tag/2.7.0');
INSERT INTO versions VALUES ('timescaledb-pg14', '2.6.1-1',  'amd', 0, '20220412', 'pg14', '', 'https://github.com/timescale/timescaledb/releases/tag/2.6.1');
INSERT INTO versions VALUES ('timescaledb-pg14', '2.5.2-1',  'amd', 0, '20220209', 'pg14', '', 'https://github.com/timescale/timescaledb/releases/tag/2.5.2');

INSERT INTO projects VALUES ('pglogical', 'hyper', 0, 'hub', 1, 'https://github.com/2ndQuadrant/pglogical/releases',
  'pglogical', 1, 'spock.png', 'Logical Replication', 'https://github.com/2ndQuadrant/pglogical');
INSERT INTO releases VALUES ('pglogical-pg13', 4, 'pglogical', 'pgLogical', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pglogical-pg14', 4, 'pglogical', 'pgLogical', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pglogical-pg13', '2.4.1-1',  'amd', 0, '20211213', 'pg13', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_1');
INSERT INTO versions VALUES ('pglogical-pg14', '2.4.1-1',  'amd', 1, '20211213', 'pg14', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_1');

INSERT INTO projects VALUES ('postgis', 'ext', 1, 'hub', 3, 'http://postgis.net/source',
  'postgis', 1, 'postgis.png', 'Spatial Extensions', 'http://postgis.net');
INSERT INTO releases VALUES ('postgis-pg13', 0, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO releases VALUES ('postgis-pg14', 0, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('postgis-pg13', '3.2.1-1', 'amd', 0, '20220212', 'pg13', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.2.1/NEWS');
INSERT INTO versions VALUES ('postgis-pg14', '3.2.1-1', 'amd', 1, '20220212', 'pg14', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.2.1/NEWS');

INSERT INTO projects VALUES ('omnidb', 'dev', 8000, '', 1, 'https://github.com/pgsql-io/omnidb-ng/tags',
  'omnidb', 0, 'omnidb.png', 'UI for Database Mgmt', 'https://github.com/pgsql-io/omnidb-ng#omnidb-ng-306');
INSERT INTO releases VALUES ('omnidb', 1, 'omnidb', 'OmniDB-NG', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('omnidb', '3.0.6', '', 1, '20220509', '', '', '');

INSERT INTO projects VALUES ('kubernetes', 'dev', 80, '', 1, 'https://github.com/ubuntu/microk8s/releases',
  'kubernetes', 0, 'kubernetes.png', 
  'Scale & Manage Containers', 
  'https://k8s.io');
INSERT INTO releases VALUES ('kubernetes', 3, 'kubernetes', 'Kubernetes', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('kubernetes', '1.22', '', 0, '20210809', '', 'UBU20', '');

INSERT INTO projects VALUES ('pgadmin', 'dev', 80, '', 1, 'https://www.pgadmin.org/news/',
  'pgadmin', 0, 'pgadmin.png', 'PostgreSQL Tools', 'https://pgadmin.org');
INSERT INTO releases VALUES ('pgadmin', 2, 'pgadmin', 'pgAdmin 4', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('pgadmin', '6.9', '', 1, '20220512', '', '', '');

INSERT INTO projects VALUES ('bulkload', 'app', 0, 'hub', 5, 'https://github.com/ossc-db/pg_bulkload/releases',
  'bulkload', 1, 'bulkload.png', 'High Speed Data Loading', 'https://github.com/ossc-db/pg_bulkload');
INSERT INTO releases VALUES ('bulkload-pg13', 6, 'bulkload', 'pgBulkLoad',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('bulkload-pg14', 6, 'bulkload', 'pgBulkLoad',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('bulkload-pg13', '3.1.19-1', 'amd', 0, '20211012', 'pg13', '', '');
INSERT INTO versions VALUES ('bulkload-pg14', '3.1.19-1', 'amd', 1, '20211012', 'pg14', '', '');

INSERT INTO projects VALUES ('repack', 'ext', 0, 'hub', 5, 'https://github.com/reorg/pg_repack/tags',
  'repack', 1, 'repack.png', 'Remove Table/Index Bloat' , 'https://github.com/reorg/pg_repack');
INSERT INTO releases VALUES ('repack-pg13', 6, 'repack', 'pgRepack',  '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('repack-pg14', 6, 'repack', 'pgRepack',  '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('repack-pg13', '1.4.7-1', 'amd', 0, '20211003', 'pg13', '', '');
INSERT INTO versions VALUES ('repack-pg14', '1.4.7-1', 'amd', 1, '20211003', 'pg14', '', '');

INSERT INTO projects VALUES ('partman', 'ext', 0, 'hub', 4, 'https://github.com/pgpartman/pg_partman/tags',
  'partman', 1, 'partman.png', 'Partition Managemnt', 'https://github.com/pgpartman/pg_partman#pg-partition-manager');
INSERT INTO releases VALUES ('partman-pg13', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('partman-pg14', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('partman-pg13', '4.6.0-1',  'amd', 0, '20211007', 'pg13', '', '');
INSERT INTO versions VALUES ('partman-pg14', '4.6.1-1',  'amd', 1, '20220415', 'pg14', '', '');
INSERT INTO versions VALUES ('partman-pg14', '4.6.0-1',  'amd', 0, '20211007', 'pg14', '', '');

INSERT INTO projects VALUES ('hypopg', 'ext', 0, 'hub', 8, 'https://github.com/HypoPG/hypopg/releases',
  'hypopg', 1, 'whatif.png', 'Hypothetical Indexes', 'https://hypopg.readthedocs.io/en/latest/');
INSERT INTO releases VALUES ('hypopg-pg13', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hypopg-pg14', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hypopg-pg13', '1.3.1-1',  'amd', 0, '20210622', 'pg13', '', '');
INSERT INTO versions VALUES ('hypopg-pg14', '1.3.1-1',  'amd', 1, '20210622', 'pg14', '', '');

INSERT INTO projects VALUES ('badger', 'app', 0, 'hub', 6, 'https://github.com/darold/pgbadger/releases',
  'badger', 0, 'badger.png', 'Performance Reporting', 'https://pgbadger.darold.net');
INSERT INTO releases VALUES ('badger', 101, 'badger','pgBadger','', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('badger', '11.8', '', 1, '20220408', '', '', '');
INSERT INTO versions VALUES ('badger', '11.7', '', 0, '20220123', '', '', '');
INSERT INTO versions VALUES ('badger', '11.6', '', 0, '20210904', '', '', '');

INSERT INTO projects VALUES ('pool2', 'hyper', 0, 'hub', 3, 'http://github.com/pgpool/pgpool2/tags',
  'pool2',  0, 'pgpool2.png', 'LoadBalancer & QueryCache', 'http://pgpool.net');
INSERT INTO releases VALUES ('pool2', 1, 'pool2',  'pgPool2', '', 'included', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('pool2', '4.3.1', 'amd', 1, '20220216', '', '', '');
INSERT INTO versions VALUES ('pool2', '4.2.8', 'amd', 0, '20220216', '', '', '');

INSERT INTO projects VALUES ('bouncer', 'hyper', 0, 'hub', 3, 'http://pgbouncer.org',
  'bouncer',  0, 'pg-bouncer.png', 'Connection Pooler', 'http://pgbouncer.org');
INSERT INTO releases VALUES ('bouncer', 2, 'bouncer',  'pgBouncer', '', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('bouncer', '1.17.0', 'amd', 1, '20220323', '', '', '');
INSERT INTO versions VALUES ('bouncer', '1.16.1', 'amd', 0, '20211111', '', '', '');

INSERT INTO projects VALUES ('patroni', 'app', 0, 'haproxy', 4, 'https://github.com/zalando/patroni/releases',
  'patroni', 0, 'patroni.png', 'HA Template', 'https://github.com/zalando/patroni');
INSERT INTO releases VALUES ('patroni', 1, 'patroni', 'Patroni', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('patroni', '2.1.4', '', 1, '20220601', '', 'UBU20', 'https://github.com/zalando/patroni/releases/tag/v2.1.4');

INSERT INTO projects VALUES ('pgjdbc', 'dev', 0, 'hub', 1, 'https://jdbc.postgresql.org', 'jdbc', 0, 'java.png', 'JDBC Driver', 'https://jdbc.postgresql.org');
INSERT INTO releases VALUES ('pgjdbc', 7, 'jdbc', 'JDBC', '', 'bring-own', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pgjdbc', '42.2.18', '', 0, '20201015', '', '',
  'https://jdbc.postgresql.org/documentation/changelog.html#version_42.2.18');

INSERT INTO projects VALUES ('npgsql', 'dev', 0, 'hub', 2, 'https://www.nuget.org/packages/Npgsql/', 'npgsql', 0, 'npgsql.png', '.NET Provider', 'https://www.npgsql.org');
INSERT INTO releases VALUES ('npgsql', 20, 'npgsql', '.net PG', '', 'bring-own', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('npgsql', '5.0.1.1', '', 0, '20201211', '', '', '');
INSERT INTO versions VALUES ('npgsql', '5.0.0', '', 0, '20201115', '', '', '');
INSERT INTO versions VALUES ('npgsql', '4.1.5', '', 0, '20200929', '', '', '');

INSERT INTO projects VALUES ('psycopg', 'dev', 0, 'hub', 3, 'https://pypi.org/project/psycopg2/', 'psycopg', 0, 'psycopg.png', 'Python Adapter', 'http://psycopg.org');
INSERT INTO releases VALUES ('psycopg', 6, 'psycopg', 'Psycopg2', '', 'bring-own', '', 1, 'LGPLv2', '', '');
INSERT INTO versions VALUES ('psycopg', '2.8.6', '', 0, '20200906', '', '', '');

INSERT INTO projects VALUES ('ruby', 'dev', 0, 'hub', 4, 'https://rubygems.org/gems/pg', 'ruby', 0, 'ruby.png', 'Ruby Interface', 'https://github.com');
INSERT INTO releases VALUES ('ruby', 7, 'ruby', 'Ruby', '', 'bring-own', '', 1, 'BSD-2', '', '');
INSERT INTO versions VALUES ('ruby', '1.2.3', '', 0, '20200318', '', '', '');

INSERT INTO projects VALUES ('psqlodbc', 'dev', 0, 'hub', 5, 'https://www.postgresql.org/ftp/odbc/versions/msi/', 'psqlodbc', 0, 'odbc.png', 'ODBC Driver', 'https://odbc.postgresql.org');
INSERT INTO releases VALUES ('psqlodbc', 2, 'psqlodbc',  'psqlODBC', '', 'test', '', 1, 'LIBGPLv2', '', '');
INSERT INTO versions VALUES ('psqlodbc', '13.01-1', 'amd', 0, '20210502', '', '', '');
INSERT INTO versions VALUES ('psqlodbc', '13.00-1', 'amd', 0, '20201119', '', '', '');

INSERT INTO projects VALUES ('ddlx',      'ext', 0, 'hub', 0, 'https://github.com/lacanoid/pgddl/releases', 'ddlx',  1, 'ddlx.png', 'DDL Extractor', 'https://github.com/lacanoid/pgddl#ddl-extractor-functions--for-postgresql');
INSERT INTO releases VALUES ('ddlx-pg13', 2, 'ddlx', 'DDLeXtact', '', 'prod','',  0, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('ddlx-pg13', '0.17-1', 'amd', 0, '20200911', 'pg13', '', '');

INSERT INTO projects VALUES ('wa',      'ext', 0, 'hub', 1, 'https://github.com/powa-team/powa/releases', 'powa',  1, 'powa.png', 'Analyzer', 'https://powa.readthedocs.io/en/latest/components/index.html');
INSERT INTO releases VALUES ('wa-pg13', 97, 'wa', 'Analyzer', '', 'test','', '', 'POSTGRES', '', '');
INSERT INTO versions VALUES ('wa-pg13', '2.1-1', 'amd', 0, '20210508', 'pg13', '', '');

INSERT INTO projects VALUES ('archivist',      'ext', 0, 'hub', 1, 'https://github.com/powa-team/powa/releases', 'archivist',  1, 'archivist.png', 'Archive Workloads', ' https://powa.readthedocs.io/en/latest/components/powa-archivist/index.html');
INSERT INTO releases VALUES ('archivist-pg13', 97, 'archivist', 'Archivist', '', 'test','',  0, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('archivist-pg13', '4.1.2-1', 'amd', 0, '20201220', 'pg13', '', '');

INSERT INTO projects VALUES ('qualstats', 'ext', 0, 'powa', 2, 'https://github.com/powa-team/pg_qualstats/releases',
  'qualstats', 1, 'qualstats.png', 'WHERE Clause Stats', 'https://github.com/powa-team/pg_qualstats');
INSERT INTO releases VALUES ('qualstats-pg13', 98, 'qualstats', 'QualStats', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('qualstats-pg13', '2.0.3-1', 'amd', 0, '20210604', 'pg13', '', '');
INSERT INTO versions VALUES ('qualstats-pg13', '2.0.2-1', 'amd', 0, '20200523', 'pg13', '', '');

INSERT INTO projects VALUES ('statkcache', 'ext', 0, 'powa', 3, 'https://github.com/powa-team/pg_stat_kcache/releases',
  'statkcache', 1, 'statkcache.png', 'Filesystem Stats', 'https://github.com/powa-team/pg_stat_kcache');
INSERT INTO releases VALUES ('statkcache-pg13', 98, 'statkcache', 'StatKcache', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('statkcache-pg13', '2.2.0-1', 'amd', 0, '20201210', 'pg13', '', '');

INSERT INTO projects VALUES ('waitsampling', 'ext', 0, 'powa', 4, 'https://github.com/postgrespro/pg_wait_sampling/releases',
  'waitsampling', 1, 'waitsampling.png', 'Stats for Wait Events', 'https://github.com/postgrespro/pg_wait_sampling');
INSERT INTO releases VALUES ('waitsampling-pg13', 98, 'waitsampling', 'WaitSampling', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('waitsampling-pg13', '1.1.3-1', 'amd', 0, '20210127', 'pg13', '', '');

INSERT INTO projects VALUES ('statmonitor', 'ext', 0, 'powa', 4, 'https://github.com/percona/pg_stat_monitor/releases',
  'statmonitor', 1, 'percona.png', 'Query Performance Monitoring', 'https://github.com/percona/pg_stat_monitor');
INSERT INTO releases VALUES ('statmonitor-pg13', 98, 'statmonitor', 'pgStatMonitor', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('statmonitor-pg13', '0.9.1-1', 'amd', 0, '20210414', 'pg13', '', '');

INSERT INTO projects VALUES ('multicorn2', 'fdw', 0, 'hub', 0, 'https://github.com/pgsql-io/multicorn2/tags',
  'multicorn2', 1, 'multicorn.png', 'Python FDW Library', 'http://multicorn2.org');
INSERT INTO releases VALUES ('multicorn2-pg13', 01, 'multicorn2', 'Multicorn2', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('multicorn2-pg14', 01, 'multicorn2', 'Multicorn2', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('multicorn2-pg13', '2.2-1', 'amd', 0, '20220419', 'pg13', '', '');
INSERT INTO versions VALUES ('multicorn2-pg13', '2.3-1', 'amd', 0, '20220509', 'pg13', '', '');
INSERT INTO versions VALUES ('multicorn2-pg14', '2.2-1', 'amd', 0, '20220419', 'pg14', '', '');
INSERT INTO versions VALUES ('multicorn2-pg14', '2.3-1', 'amd', 1, '20220509', 'pg14', '', '');
