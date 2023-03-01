
DROP VIEW  IF EXISTS v_grp_cats;
DROP VIEW  IF EXISTS v_versions;

DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS releases;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS categories;
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
INSERT INTO grp_cats VALUES ('pg',    1, 'pg',  'postgres-core',       'Postgres',        'PostgreSQL&reg;');
INSERT INTO grp_cats VALUES ('pge',   1, 'pgc', 'postgres-pgedge',     'pgEdge',          'pgEdge');
INSERT INTO grp_cats VALUES ('fdw',   2, 'pgc', 'postgres-fdws',       'PG FDWs',         'Foreign Data Wrappers');
INSERT INTO grp_cats VALUES ('ext',   3, 'pgc', 'postgres-extensions', 'PG Extensions',   'Extensions');
INSERT INTO grp_cats VALUES ('app',   4, 'pgc', 'postgres-apps',       'PG Applications', 'Applications');
INSERT INTO grp_cats VALUES ('dev',   5, 'pgc', 'postgres-devs',       'PG DevOps',       'For Developers');
INSERT INTO grp_cats VALUES ('strm',  2, 'ods', 'change-data-capture', 'Streaming & CDC', 'Streaming & Change Data Capture');

CREATE VIEW v_grp_cats AS
   SELECT g.sort_order as grp_sort, c.sort_order as cat_sort,
          g.grp, g.short_desc as grp_short_desc, c.grp_cat, c.web_page, c.page_title,
          c.short_desc as grp_cat_desc
     FROM grps g, grp_cats c
    WHERE g.grp = c.grp
 ORDER BY 1, 2;


CREATE TABLE categories (
  category    INTEGER  NOT NULL PRIMARY KEY,
  sort_order  SMALLINT NOT NULL,
  description TEXT     NOT NULL,
  short_desc  TEXT     NOT NULL
);


CREATE TABLE projects (
  project   	 TEXT     NOT NULL PRIMARY KEY,
  grp_cat        TEXT     NOT NULL,
  category  	 INTEGER  NOT NULL,
  port      	 INTEGER  NOT NULL,
  depends   	 TEXT     NOT NULL,
  start_order    INTEGER  NOT NULL,
  sources_url    TEXT     NOT NULL,
  short_name     TEXT     NOT NULL,
  is_extension   SMALLINT NOT NULL,
  image_file     TEXT     NOT NULL,
  description    TEXT     NOT NULL,
  project_url    TEXT     NOT NULL,
  FOREIGN KEY (category) REFERENCES categories(category)
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

INSERT INTO categories VALUES (0,   0, 'Hidden', 'NotShown');
INSERT INTO categories VALUES (1,  10, 'Rock-solid Postgres', 'Postgres');
INSERT INTO categories VALUES (11, 30, 'Clustering', 'Cloud');
INSERT INTO categories VALUES (10, 15, 'Streaming Change Data Capture', 'CDC');
INSERT INTO categories VALUES (2,  12, 'Legacy RDBMS', 'Legacy');
INSERT INTO categories VALUES (6,  20, 'Oracle Migration & Compatibility', 'OracleMig');
INSERT INTO categories VALUES (4,  11, 'Postgres Apps & Extensions', 'Extras');
INSERT INTO categories VALUES (5,  25, 'Data Integration', 'Integration');
INSERT INTO categories VALUES (3,  80, 'Database Developers', 'Developers');
INSERT INTO categories VALUES (9,  87, 'Management & Monitoring', 'Manage/Monitor');

-- ## HUB ################################
INSERT INTO projects VALUES ('hub', 'app', 0, 0, 'hub', 0, 'https://github.com/pgedge/nodectl','',0,'','','');
INSERT INTO releases VALUES ('hub', 1, 'hub', '', '', 'hidden', '', 1, '', '', '');
INSERT INTO versions VALUES ('hub', '23.03-3', '',  1, '20230301', '', '', '');
INSERT INTO versions VALUES ('hub', '23.03-2', '',  0, '20230225', '', '', '');

-- ##
INSERT INTO projects VALUES ('pg', 'pge', 1, 5432, 'hub', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org');

INSERT INTO releases VALUES ('pg11', 4, 'pg', 'PostgreSQL', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/11/release-11.html>2018</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg11', '11.19-1', 'el8', 1, '20230209', '', '', '');

INSERT INTO releases VALUES ('pg12', 3, 'pg', 'PostgreSQL', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/12/release-12.html>2019</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg12', '12.14-1', 'el8', 1, '20230209', '', '', '');

INSERT INTO releases VALUES ('pg13', 2, 'pg', '', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/13/release-13.html>2.21</a></font>',
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg13', '13.10-1', 'el8', 1, '20230209','', '', '');

INSERT INTO releases VALUES ('pg14', 1, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/14/release-14.html>2021</a></font>',
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg14', '14.7-1', 'el8, arm', 1, '20230209','', '', '');
INSERT INTO versions VALUES ('pg14', '14.6-1', 'el8, arm',      0, '20221110','', '', '');

INSERT INTO releases VALUES ('pg15', 2, 'pg', '', '', 'prod', 
  '<font size=-1 color=red><b>New in <a href=https://sql-info.de/postgresql/postgresql-15/articles-about-new-features-in-postgresql-15.html>2022!</a></b></font>',
  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg15', '15.2-1',  'el8, arm, osx', 1, '20230209','', '', '');
INSERT INTO versions VALUES ('pg15', '15.1-4',  'el8, arm, osx', 0, '20230106','', '', '');

INSERT INTO projects VALUES ('debezium', 'strm', 10, 8083, '', 3, 'https://debezium.io/releases/1.9/',
  'Debezium', 0, 'debezium.png', 'Heterogeneous CDC', 'https://debezium.io');
INSERT INTO releases VALUES ('debezium', 1, 'debezium', 'Debezium', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('debezium', '1.9.2.Final',   '', 0, '20220520', '', '', '');

INSERT INTO projects VALUES ('olr', 'strm', 10, 8083, '', 3, 'https://github.com/bersler/OpenLogReplicator/releases',
  'OLR', 0, 'olr.png', 'Oracle Binary Log Replicator', 'https://www.bersler.com/openlogreplicator');
INSERT INTO releases VALUES ('olr', 3, 'olr', 'OLR', '', 'test', '', 1, 'GPL', '', '');
INSERT INTO versions VALUES ('olr', '0.9.41-beta',   '', 0, '20220328', '', '', '');
INSERT INTO versions VALUES ('olr', '0.9.40-beta',   '', 0, '2022.214', '', '', '');

INSERT INTO projects VALUES ('kafka', 'strm', 10, 9092, '', 2, 'https://kafka.apache.org/downloads',
  'Kafka', 0, 'kafka.png', 'Streaming Platform', 'https://kafka.apache.org');
INSERT INTO releases VALUES ('kafka', 0, 'kafka', 'Apache Kafka', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('kafka', '3.2.0', '', 0, '20220517', '', '', 'https://downloads.apache.org/kafka/3.2.0/RELEASE_NOTES.html');

INSERT INTO projects VALUES ('redis', 'nosql', 2, 6379, 'hub', 2, 'https://github.com/redis/redis/tags',
  'Redis', 0, 'redis.png', 'In-Memory DataStore', 'https://redis.io');
INSERT INTO releases VALUES ('redis', 6, 'redis', 'Redis 6.2.6', '', 'test', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('redis', '6.2', '', 0, '20211004', '', '', '');

INSERT INTO projects VALUES ('memcached', 'nosql',  2, 6379, 'hub', 2, 'http://memcached.org/downloads',
  'Memcached', 0, 'memcached.png', 'In-Memory Cache', 'http://memcached.org');
INSERT INTO releases VALUES ('memcached', 3, 'memcached', 'Memached 1.6.12', '', 'test', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('memcached', '1.6', '', 0, '20210928', '', '', '');

INSERT INTO projects VALUES ('apicurio', 'strm', 10, 8080, 'hub', 1, 'https://github.com/apicurio/apicurio-registry/releases',
  'apicurio', 0, 'apicurio.png', 'Schema Registry', 'https://www.apicur.io/registry/');
INSERT INTO releases VALUES ('apicurio', 3, 'apicurio', 'Apicurio', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.3', '',  0, '20220414', '', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.2', '',  0, '20220328', '', '', '');

INSERT INTO projects VALUES ('zookeeper', 'nosql', 10, 2181, 'hub', 1, 'https://zookeeper.apache.org/releases.html#releasenotes',
  'zookeeper', 0, 'zookeeper.png', 'Distributed Key-Store for HA', 'https://zookeeper.apache.org');
INSERT INTO releases VALUES ('zookeeper', 3, 'zookeeper', 'Zookeeper', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('zookeeper', '3.7.0', '',  0, '20210327', '', '',
  'https://zookeeper.apache.org/doc/r3.7.0/releasenotes.html');

INSERT INTO projects VALUES ('decoderbufs', 'strm', 10, 0, 'hub', 0, 'https://github.com/debezium/postgres-decoderbufs', 
  'decoderbufs', 1, 'protobuf.png', 'Logical decoding via ProtoBuf', 'https://github.com/debezium/postgres-decoderbufs');
INSERT INTO releases VALUES ('decoderbufs-pg14',  4, 'decoderbufs', 'DecoderBufs', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('decoderbufs-pg14', '1.7.0-1', 'arm, el8', 0, '20211001', 'pg14', '', '');

INSERT INTO projects VALUES ('mongofdw', 'fdw', 5, 0, 'hub', 0, 'https://github.com/EnterpriseDB/mongo_fdw/tags', 
  'mongofdw', 1, 'mongodb.png', 'MongoDB from PG', 'https://github.com/EnterpriseDB/mongo_fdw#mongo_fdw');
INSERT INTO releases VALUES ('mongofdw-pg14',  3, 'mongofdw', 'MongoFDW', '', 'prod', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('mongofdw-pg14', '5.4.0-1', 'el8', 0, '20220519', 'pg14', '', '');

INSERT INTO projects VALUES ('mysqlfdw', 'fdw', 5, 0, 'hub', 0, 'https://github.com/EnterpriseDB/mysql_fdw/tags', 
  'mysqlfdw', 1, 'mysql.png', 'MySQL & MariaDB from PG', 'https://github.com/EnterpriseDb/mysql_fdw');
INSERT INTO releases VALUES ('mysqlfdw-pg14',  4, 'mysqlfdw', 'MySQL FDW',  '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('mysqlfdw-pg14', '2.8.0-1', 'el8, arm', 0, '20220516', 'pg14', '', '');

INSERT INTO projects VALUES ('tdsfdw', 'fdw', 5, 0, 'hub', 0, 'https://github.com/tds-fdw/tds_fdw/tags',
  'tdsfdw', 1, 'tds.png', 'SQL Svr & Sybase from PG', 'https://github.com/tds-fdw/tds_fdw/#tds-foreign-data-wrapper');
INSERT INTO releases VALUES ('tdsfdw-pg15', 4, 'tdsfdw', 'TDS FDW', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('tdsfdw-pg15', '2.0.3-1', 'el8', 1, '20221022', 'pg15', '', 'https://github.com/tds-fdw/tds_fdw/releases/tag/v2.0.3');

INSERT INTO projects VALUES ('bqfdw', 'fdw', 5, 0, 'multicorn2', 1, 'https://pypi.org/project/bigquery-fdw/#history',
  'bqfdw', 1, 'bigquery.png', 'BigQuery from PG', 'https://pypi.org/project/bigquery-fdw');
INSERT INTO releases VALUES ('bqfdw-pg14',  3, 'bqfdw', 'BigQueryFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('bqfdw-pg14', '1.9', 'amd',  0, '20211218', 'pg14', '', '');

INSERT INTO projects VALUES ('esfdw', 'fdw', 5, 0, 'multicorn2', 1, 'https://pypi.org/project/pg-es-fdw/#history',
  'esfdw', 1, 'esfdw.png', 'ElasticSearch from PG', 'https://pypi.org/project/pg-es-fdw/');
INSERT INTO releases VALUES ('esfdw-pg15',  4, 'esfdw', 'ElasticSearchFDW', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('esfdw-pg15', '0.11.2', 'amd',  1, '20220918', 'pg15', '', '');

INSERT INTO projects VALUES ('ora2pg', 'dev', 6, 0, 'hub', 0, 'https://github.com/darold/ora2pg/tags',
  'ora2pg', 0, 'ora2pg.png', 'Migrate from Oracle to PG', 'https://ora2pg.darold.net');
INSERT INTO releases VALUES ('ora2pg', 2, 'ora2pg', 'Oracle to PG', '', 'test', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('ora2pg', '23.1', '', 0, '20220512', '', '', 'https://github.com/darold/ora2pg/releases/tag/v23.1');

INSERT INTO projects VALUES ('oraclefdw', 'fdw', 6, 0, 'hub', 0, 'https://github.com/laurenz/oracle_fdw/tags',
  'oraclefdw', 1, 'oracle_fdw.png', 'Oracle from PG', 'https://github.com/laurenz/oracle_fdw');
INSERT INTO releases VALUES ('oraclefdw-pg15', 2, 'oraclefdw', 'OracleFDW', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('oraclefdw-pg15','2.5.0-1', 'el8', 1, '20221028', 'pg15', '', 'https://github.com/laurenz/oracle_fdw/releases/tag/ORACLE_FDW_2_5_0');

INSERT INTO projects VALUES ('instantclient', 'sql', 6, 0, 'hub', 0, 'https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html', 
  'instantclient', 0, 'instantclient.png', 'Oracle Instant Client', 'https://www.oracle.com/database/technologies/instant-client.html');
INSERT INTO releases VALUES ('instantclient', 2, 'instantclient', 'Instant Client', '', 'test','', 0, 'ORACLE', '', '');
INSERT INTO versions VALUES ('instantclient', '21.6', '', 0, '20220420', '', '', '');

INSERT INTO projects VALUES ('orafce', 'ext', 4, 0, 'hub', 0, 'https://github.com/orafce/orafce/releases',
  'orafce', 1, 'larry.png', 'Ora Built-in Packages', 'https://github.com/orafce/orafce#orafce---oracles-compatibility-functions-and-packages');
INSERT INTO releases VALUES ('orafce-pg15', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('orafce-pg15', '4.1.1-1',   'arm, el8', 1, '20230127', 'pg15', '', '');
INSERT INTO versions VALUES ('orafce-pg15', '4.1.0-1',   'arm, el8', 0, '20230107', 'pg15', '', '');

INSERT INTO projects VALUES ('fixeddecimal', 'ext', 6, 0, 'hub', 0, 'https://github.com/pgsql-io/fixeddecimal/tags',
  'fixeddecimal', 1, 'fixeddecimal.png', 'Much faster than NUMERIC', 'https://github.com/pgsql-io/fixeddecimal');
INSERT INTO releases VALUES ('fixeddecimal-pg14', 90, 'fixeddecimal', 'FixedDecimal', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('fixeddecimal-pg14', '1.1.0-1',  'amd', 0, '2.211119', 'pg14', '', '');

INSERT INTO projects VALUES ('plv8', 'dev', 3, 0, 'hub', 0, 'https://github.com/plv8/plv8/tags',
  'plv8',   1, 'v8.png', 'Javascript Stored Procedures', 'https://github.com/plv8/plv8');
INSERT INTO releases VALUES ('plv8-pg14', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plv8-pg14', '3.1.2-1', 'el8', 0, '2.210721', 'pg14', '', '');

INSERT INTO projects VALUES ('plpython', 'dev', 3, 0, 'hub', 0, 'https://www.postgresql.org/docs/13/plpython.html',
  'plpython', 1, 'python.png', 'Python3 Stored Procedures', 'https://www.postgresql.org/docs/13/plpython.html');
INSERT INTO releases VALUES ('plpython3', 5, 'plpython', 'PL/Python','', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plpython3', '15', 'arm, el8', 1, '2.210213', 'pg15', '', '');

INSERT INTO projects VALUES ('plperl', 'dev', 3, 0, 'hub', 0, 'https://www.postgresql.org/docs/13/plperl.html',
	'plperl', 1, 'perl.png', 'Perl Stored Procedures', 'https://www.postgresql.org/docs/13/plperl.html');
INSERT INTO releases VALUES ('plperl', 6, 'plperl', 'PL/Perl','', 'included', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plperl', '15', 'arm, el8', 1, '2.210213', 'pg15', '', '');

INSERT INTO projects VALUES ('pljava', 'dev', 3, 0, 'hub', 0, 'https://github.com/tada/pljava/releases', 
  'pljava', 1, 'pljava.png', 'Java Stored Procedures', 'https://github.com/tada/pljava');
INSERT INTO releases VALUES ('pljava-pg13', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pljava-pg13', '1.6.2-1',  'amd',  1, '20211127', 'pg13', '', '');

INSERT INTO projects VALUES ('pldebugger', 'dev', 3, 0, 'hub', 0, 'https://github.com/EnterpriseDB/pldebugger/tags',
  'pldebugger', 1, 'debugger.png', 'Stored Procedure Debugger', 'https://github.com/EnterpriseDB/pldebugger');
INSERT INTO releases VALUES ('pldebugger-pg15', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pldebugger-pg15', '1.5-1',  'arm, el8',  1, '20220720', 'pg15', '', '');

INSERT INTO projects VALUES ('plprofiler', 'dev', 3, 0, 'hub', 7, 'https://github.com/bigsql/plprofiler/tags',
  'plprofiler', 1, 'plprofiler.png', 'Stored Procedure Profiler', 'https://github.com/bigsql/plprofiler#plprofiler');
INSERT INTO releases VALUES ('plprofiler-pg15', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plprofiler-pg15', '4.2-1', 'arm, el8', 1, '20221003', 'pg15', '', '');

INSERT INTO projects VALUES ('golang', 'dev', 4, 0, 'hub', 0, 'https://go.dev/dl',
  'golang', 0, 'go.png', 'Fast & Scaleable Programming', 'https://go.dev');
INSERT INTO releases VALUES ('golang', 9, 'golang', 'GO', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('golang', '1.19.3', '', 0, '20221101', '', '', '');

INSERT INTO projects VALUES ('postgrest', 'pge', 4, 3000, 'hub', 0, 'https://github.com/postgrest/postgrest/tags',
  'postgrest', 0, 'postgrest.png', 'a RESTful API', 'https://postgrest.org');
INSERT INTO releases VALUES ('postgrest', 9, 'postgrest', 'PostgREST', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('postgrest', '10.1.1', 'arm, el8', 1, '20221121', '', '', 'https://postgrest.org');

INSERT INTO projects VALUES ('prompgexp', 'pge', 4, 9187, 'golang', 0, 'https://github.com/prometheus-community/postgres_exporter/tags',
  'prompgexp', 0, 'prometheus.png', 'Prometheus PG Exporter', 'https://github.com/prometheus-community/postgres_exporter');
INSERT INTO releases VALUES ('prompgexp', 9, 'prompgexp', 'Prometheus PG Exporter', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('prompgexp', '0.11.1', '', 0, '20220720', '', '', 'https://github.com/prometheus-community/postgres_exporter');

INSERT INTO projects VALUES ('nodejs', 'app', 4, 3000, 'hub', 0, 'https://github.com/',
  'nodejs', 0, 'nodejs.png', 'Javascrip Runtime', 'https://nodejs.org');
INSERT INTO releases VALUES ('nodejs', 9, 'nodejs', 'Node.js', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('nodejs', '18.12.1', '', 0, '20221104', '', '', 'https://nodejs.org');

INSERT INTO projects VALUES ('audit', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgaudit/pgaudit/releases',
  'audit', 1, 'audit.png', 'Audit Logging', 'https://github.com/pgaudit/pgaudit');
INSERT INTO releases VALUES ('audit-pg15', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('audit-pg15', '1.7.0-1', 'arm, el8', 1, '20221013', 'pg15', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.7.0');

INSERT INTO projects VALUES ('hintplan', 'ext', 6, 0, 'hub', 0, 'https://github.com/ossc-db/pg_hint_plan/tags',
  'hintplan', 1, 'hintplan.png', 'Execution Plan Hints', 'https://github.com/ossc-db/pg_hint_plan');
INSERT INTO releases VALUES ('hintplan-pg15', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hintplan-pg15', '1.5.0-1', 'arm, el8', 1, '20230128', 'pg15', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.5.0');

INSERT INTO projects VALUES ('anon', 'ext', 4, 0, 'ddlx', 1, 'https://gitlab.com/dalibo/postgresql_anonymizer/-/tags',
  'anon', 1, 'anon.png', 'Anonymization & Masking', 'https://gitlab.com/dalibo/postgresql_anonymizer/blob/master/README.md');
INSERT INTO releases VALUES ('anon-pg15', 11, 'anon', 'Anonymizer', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('anon-pg15', '1.1.0-1', 'arm, el8', 0, '20220928', 'pg15', '', '');

INSERT INTO projects VALUES ('citus', 'ext', 4, 0, 'hub',0, 'https://github.com/citusdata/citus/releases',
  'citus', 1, 'citus.png', 'Distributed PostgreSQL', 'https://github.com/citusdata/citus');
INSERT INTO releases VALUES ('citus-pg15',  0, 'citus', 'Citus', '', 'test', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('citus-pg15', '11.2.0-1', 'el8, arm', 1, '20230206', 'pg15', '', 'https://github.com/citusdata/citus/releases/tag/v11.2.0');
INSERT INTO versions VALUES ('citus-pg15', '11.1.5-1', 'el8, arm', 0, '20221212', 'pg15', '', 'https://github.com/citusdata/citus/releases/tag/v11.1.5');

INSERT INTO projects VALUES ('cron', 'ext', 4, 0, 'hub',0, 'https://github.com/citusdata/pg_cron/releases',
  'cron', 1, 'cron.png', 'Background Job Scheduler', 'https://github.com/citusdata/pg_cron');
INSERT INTO releases VALUES ('cron-pg15', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('cron-pg15', '1.5.1-1', 'el8, arm', 1, '20230215', 'pg15', '', '');
INSERT INTO versions VALUES ('cron-pg15', '1.4.2-1', 'el8, arm', 0, '20220714', 'pg15', '', '');

INSERT INTO projects VALUES ('background', 'ext', 4, 0, 'hub',0, 'https://github.com/oscg-io/background/tags',
  'background', 1, 'background.png', 'Background Worker', 'https://github.com/oscg-io/background');
INSERT INTO releases VALUES ('background-pg14', 10, 'background', 'Background', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('background-pg14', '1.1-1', 'el8, arm', 0, '20220804', 'pg14', '', '');

INSERT INTO projects VALUES ('timescaledb', 'ext', 4, 0, 'hub', 1, 'https://github.com/timescale/timescaledb/releases',
   'timescaledb', 1, 'timescaledb.png', 'Time Series Data', 'https://github.com/timescale/timescaledb/#timescaledb');
INSERT INTO releases VALUES ('timescaledb-pg14',  2, 'timescaledb', 'TimescaleDB', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('timescaledb-pg14', '2.8.0-1',  'el8, arm', 0, '20220831', 'pg14', '', 'https://github.com/timescale/timescaledb/releases/tag/2.8.0');

INSERT INTO projects VALUES ('spock', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/spock/tags',
  'spock', 1, 'spock.png', 'Logical & Multi-Active Replication', 'https://github.com/pgedge/spock/#spock');
INSERT INTO releases VALUES ('spock-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('spock-pg15', '3.0.18-1', 'el8, arm, osx', 1, '20230217', 'pg15', '', '');
INSERT INTO versions VALUES ('spock-pg15', '3.0.17-1', 'el8, arm, osx', 0, '20230209', 'pg15', '', '');

INSERT INTO projects VALUES ('pglogical', 'ext', 4, 0, 'hub', 1, 'https://github.com/2ndQuadrant/pglogical/releases',
  'pglogical', 1, 'spock.png', 'Logical Replication', 'https://github.com/2ndQuadrant/pglogical');
INSERT INTO releases VALUES ('pglogical-pg14', 4, 'pglogical', 'pgLogical', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pglogical-pg15', 4, 'pglogical', 'pgLogical', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pglogical-pg14', '2.4.2-1',  'arm, el8', 0, '20221021', 'pg14', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_2');
INSERT INTO versions VALUES ('pglogical-pg15', '2.4.2-1',  'arm, el8', 0, '20221021', 'pg15', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_2');

INSERT INTO projects VALUES ('postgis', 'ext', 4, 1, 'hub', 3, 'http://postgis.net/source',
  'postgis', 1, 'postgis.png', 'Spatial Extensions', 'http://postgis.net');
INSERT INTO releases VALUES ('postgis-pg15', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('postgis-pg15', '3.3.2-1', 'arm', 1, '20221112', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.3.2/NEWS');
INSERT INTO versions VALUES ('postgis-pg15', '3.3.1-1', 'arm', 0, '20220909', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.3.1/NEWS');

INSERT INTO projects VALUES ('omnidb', 'app', 6, 8000, '', 1, 'https://github.com/pgsql-io/omnidb-ng/tags',
  'omnidb', 0, 'omnidb.png', 'UI for Database Mgmt', 'https://github.com/pgsql-io/omnidb-ng#omnidb-ng-306');
INSERT INTO releases VALUES ('omnidb', 1, 'omnidb', 'OmniDB-NG', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('omnidb', '3.0.6', '', 0, '20220509', '', '', '');

INSERT INTO projects VALUES ('pgadmin', 'app', 3, 80, '', 1, 'https://www.pgadmin.org/news/',
  'pgadmin', 0, 'pgadmin.png', 'PostgreSQL Tools', 'https://pgadmin.org');
INSERT INTO releases VALUES ('pgadmin', 2, 'pgadmin', 'pgAdmin 4', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('pgadmin', '6.9', '', 0, '20220512', '', '', '');

INSERT INTO projects VALUES ('bulkload', 'ext', 4, 0, 'hub', 5, 'https://github.com/ossc-db/pg_bulkload/releases',
  'bulkload', 1, 'bulkload.png', 'High Speed Data Loading', 'https://github.com/ossc-db/pg_bulkload');
INSERT INTO releases VALUES ('bulkload-pg14', 6, 'bulkload', 'pgBulkLoad',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('bulkload-pg14', '3.1.19-1', 'arm, el8', 0, '20211012', 'pg14', '', '');

INSERT INTO projects VALUES ('repack', 'ext', 4, 0, 'hub', 5, 'https://github.com/reorg/pg_repack/tags',
  'repack', 1, 'repack.png', 'Remove Table/Index Bloat' , 'https://github.com/reorg/pg_repack');
INSERT INTO releases VALUES ('repack-pg15', 6, 'repack', 'pgRepack',  '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('repack-pg15', '1.4.8-1', 'arm, el8', 1, '20221019', 'pg15', '', '');

INSERT INTO projects VALUES ('partman', 'ext', 4, 0, 'hub', 4, 'https://github.com/pgpartman/pg_partman/tags',
  'partman', 1, 'partman.png', 'Partition Management', 'https://github.com/pgpartman/pg_partman#pg-partition-manager');
INSERT INTO releases VALUES ('partman-pg15', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('partman-pg15', '4.7.2-1',  'arm, el8', 1, '20221216', 'pg15', '', '');
INSERT INTO versions VALUES ('partman-pg15', '4.7.1-1',  'arm, el8', 0, '20221013', 'pg15', '', '');

INSERT INTO projects VALUES ('hypopg', 'ext', 4, 0, 'hub', 8, 'https://github.com/HypoPG/hypopg/releases',
  'hypopg', 1, 'whatif.png', 'Hypothetical Indexes', 'https://hypopg.readthedocs.io/en/latest/');
INSERT INTO releases VALUES ('hypopg-pg14', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hypopg-pg14', '1.3.1-1',  'arm, el8', 0, '20210622', 'pg14', '', '');

INSERT INTO projects VALUES ('badger', 'app', 4, 0, 'hub', 6, 'https://github.com/darold/pgbadger/releases',
  'badger', 0, 'badger.png', 'Performance Reporting', 'https://pgbadger.darold.net');
INSERT INTO releases VALUES ('badger', 101, 'badger','pgBadger','', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('badger', '11.8', '', 0, '20220408', '', '', '');

INSERT INTO projects VALUES ('pool2', 'ext', 4, 0, 'hub', 3, 'http://github.com/pgpool/pgpool2/tags',
  'pool2',  0, 'pgpool2.png', 'QueryCache', 'http://pgpool.net');
INSERT INTO releases VALUES ('pool2', 1, 'pool2',  'pgPool2', '', 'test', '', 1, 'BSD', '', '');
INSERT INTO versions VALUES ('pool2', '4.4.0', 'el8, arm', 0, '2022.216', '', '', '');

INSERT INTO projects VALUES ('nginx', 'app', 4, 443, 'hub', 3, 'http://nginx.org',
  'nginx',  0, 'pg-nginx.png', 'HTTPS & Reverse Proxy Server', 'http://nginx.org');
INSERT INTO releases VALUES ('nginx', 2, 'nginx',  'NGINX', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('nginx', '1-1', '', 0, '20221215', '', '', '');

INSERT INTO projects VALUES ('bouncer', 'pge', 4, 5433, 'hub', 3, 'http://pgbouncer.org',
  'bouncer',  0, 'pg-bouncer.png', 'Connection Pooler', 'http://pgbouncer.org');
INSERT INTO releases VALUES ('bouncer', 2, 'bouncer',  'pgBouncer', '', 'prod', '', 1, 'ISC', '', '');
INSERT INTO versions VALUES ('bouncer', '1.18.0-1', 'el8, arm', 1, '20221212', '', '', '');

INSERT INTO projects VALUES ('pgedge', 'pge', 0, 0, 'hub', 3, 'http://pgedge.org',
  'pgedge',  0, 'pgedge.png', 'Multi-Active Global Postgres Clusters', 'http://pgedge.com');
INSERT INTO releases VALUES ('pgedge', 1, 'pgedge',  'pgEdge', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('pgedge', '15.2.1', '', 1, '20230220', '', '', '');
INSERT INTO versions VALUES ('pgedge', '15.2',   '', 0, '20230209', '', '', '');
INSERT INTO versions VALUES ('pgedge', '15.1',   '', 0, '20230126', '', '', '');

INSERT INTO projects VALUES ('pgdiff', 'pge', 4, 0, 'csvdiff', 3, 'https://github.com/pgedge/pgdiff/tags',
  'pgdiff',  0, 'pgdiff.png', 'pgdiff', 'https://github.com/pgedge/pgdiff');
INSERT INTO releases VALUES ('pgdiff', 2, 'pgdiff',  'PG Diff', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('pgdiff', '1.1', '', 1, '20230215', '', '', '');

INSERT INTO projects VALUES ('csvdiff', 'pge', 0, 0, 'hub', 3, 'https://github.com/luss/csvdiff/tags',
  'csvdiff',  0, 'csvdiff.png', 'csvdiff', 'https://github.com/luss/csvdiff');
INSERT INTO releases VALUES ('csvdiff', 2, 'csvdiff',  'CSV Diff', '', 'prod', '', 1, '', '', '');
INSERT INTO versions VALUES ('csvdiff', '1.4.0', 'el8, arm, osx', 1, '20230206', '', '', '');

INSERT INTO projects VALUES ('backrest', 'pge', 4, 0, 'hub', 3, 'http://pgbackrest.org',
  'backrest',  0, 'backrest.png', 'Backup & Restore', 'http://pgbackrest.org');
INSERT INTO releases VALUES ('backrest', 2, 'backrest',  'pgBackRest', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('backrest', '2.44-1', 'el8, arm', 1, '20230129', '', '', '');

INSERT INTO projects VALUES ('patroni', 'app', 11, 0, 'haproxy', 4, 'https://github.com/zalando/patroni/releases',
  'patroni', 0, 'patroni.png', 'HA Template', 'https://github.com/zalando/patroni');
INSERT INTO releases VALUES ('patroni', 1, 'patroni', 'Patroni', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('patroni', '2.1.1', '', 0, '20210819', '', '', 'https://github.com/zalando/patroni/releases/tag/v2.1.1');

INSERT INTO projects VALUES ('ddlx', 'ext',     4, 0, 'hub', 0, 'https://github.com/lacanoid/pgddl/releases', 'ddlx',  1, 'ddlx.png', 'DDL Extractor', 'https://github.com/lacanoid/pgddl#ddl-extractor-functions--for-postgresql');
INSERT INTO releases VALUES ('ddlx-pg13', 2, 'ddlx', 'DDLeXtact', '', 'prod','',  0, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('ddlx-pg13', '0.17-1', 'amd', 1, '2.210911', 'pg13', '', '');

INSERT INTO projects VALUES ('multicorn2', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgsql-io/multicorn2/tags',
  'multicorn2', 1, 'multicorn.png', 'Python FDW Library', 'http://multicorn2.org');
INSERT INTO releases VALUES ('multicorn2-pg15', 1, 'multicorn2', 'Multicorn2', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('multicorn2-pg15', '2.4-1', 'arm, el8', 1, '20220909', 'pg15', '', '');
