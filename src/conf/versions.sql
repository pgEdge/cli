DROP VIEW  IF EXISTS v_grp_cats;
DROP VIEW  IF EXISTS v_versions;

DROP TABLE IF EXISTS locations;
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
INSERT INTO versions VALUES ('hub', '23.131', '',  1, '20230928', '', '', '');
INSERT INTO versions VALUES ('hub', '23.130', '',  0, '20230927', '', '', '');
INSERT INTO versions VALUES ('hub', '23.129', '',  0, '20230914', '', '', '');
INSERT INTO versions VALUES ('hub', '23.128', '',  0, '20230829', '', '', '');
INSERT INTO versions VALUES ('hub', '23.127', '',  0, '20230810', '', '', '');
INSERT INTO versions VALUES ('hub', '23.126', '',  0, '20230803', '', '', '');

-- ##
INSERT INTO projects VALUES ('pg', 'pge', 1, 5432, 'hub', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org');

INSERT INTO releases VALUES ('pg11', 4, 'pg', 'PostgreSQL', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/11/release-11.html>2018</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg11', '11.21-1', 'el8', 1, '20230810', '', '', '');
INSERT INTO versions VALUES ('pg11', '11.20-1', 'el8', 0, '20230511', '', '', '');

INSERT INTO releases VALUES ('pg12', 3, 'pg', 'PostgreSQL', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/12/release-12.html>2019</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg12', '12.16-1', 'el8', 1, '20230810', '', '', '');
INSERT INTO versions VALUES ('pg12', '12.15-1', 'el8', 0, '20230511', '', '', '');

INSERT INTO releases VALUES ('pg13', 2, 'pg', '', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/13/release-13.html>2020</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg13', '13.12-1', 'el8', 1, '20230810','', '', '');
INSERT INTO versions VALUES ('pg13', '13.11-1', 'el8', 0, '20230511','', '', '');

INSERT INTO releases VALUES ('pg14', 1, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/14/release-14.html>2021</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg14', '14.9-1', 'el8', 1, '20230810','', '', '');
INSERT INTO versions VALUES ('pg14', '14.8-1', 'el8', 0, '20230511','', '', '');

INSERT INTO releases VALUES ('pg15', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/15/release-15.html>2022</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg15', '15.4-2',  'el8, el9, arm9',      1, '20230829','', '', '');
INSERT INTO versions VALUES ('pg15', '15.4-1',  'el8, el9, arm9',      0, '20230810','', '', '');
INSERT INTO versions VALUES ('pg15', '15.3-2',  'el8, el9, arm9',      0, '20230608','', '', '');

INSERT INTO releases VALUES ('pg16', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/16/release-16.html>2023!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg16', '16.0-1',    'el9, arm9', 1, '20230914','', '', '');

INSERT INTO releases VALUES ('pg17', 2, 'pg', '', '', 'test', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/17/release-17.html>2024!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg17', '17devel-1', 'el9, arm9', 1, '20230927','', '', '');

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

INSERT INTO projects VALUES ('apicurio', 'strm', 10, 8080, 'hub', 1, 'https://github.com/apicurio/apicurio-registry/releases',
  'apicurio', 0, 'apicurio.png', 'Schema Registry', 'https://www.apicur.io/registry/');
INSERT INTO releases VALUES ('apicurio', 3, 'apicurio', 'Apicurio', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.3', '',  0, '20220414', '', '', '');
INSERT INTO versions VALUES ('apicurio', '2.2.2', '',  0, '20220328', '', '', '');

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
INSERT INTO versions VALUES ('tdsfdw-pg15', '2.0.3-1', 'el8', 0, '20221022', 'pg15', '', 'https://github.com/tds-fdw/tds_fdw/releases/tag/v2.0.3');

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
INSERT INTO releases VALUES ('oraclefdw-pg15', 2, 'oraclefdw', 'OracleFDW', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('oraclefdw-pg16', 2, 'oraclefdw', 'OracleFDW', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('oraclefdw-pg15','2.6.0-1', 'el9', 1, '20230914', 'pg15', '', 'https://github.com/laurenz/oracle_fdw/releases/tag/ORACLE_FDW_2_6_0');
INSERT INTO versions VALUES ('oraclefdw-pg16','2.6.0-1', 'el9', 1, '20230914', 'pg16', '', 'https://github.com/laurenz/oracle_fdw/releases/tag/ORACLE_FDW_2_6_0');

INSERT INTO projects VALUES ('instantclient', 'sql', 6, 0, 'hub', 0, 'https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html', 
  'instantclient', 0, 'instantclient.png', 'Oracle Instant Client', 'https://www.oracle.com/database/technologies/instant-client.html');
INSERT INTO releases VALUES ('instantclient', 2, 'instantclient', 'Instant Client', '', 'test','', 0, 'ORACLE', '', '');
INSERT INTO versions VALUES ('instantclient', '21.11', '', 0, '20230914', '', '', '');

INSERT INTO projects VALUES ('orafce', 'ext', 4, 0, 'hub', 0, 'https://github.com/orafce/orafce/releases',
  'orafce', 1, 'larry.png', 'Ora Built-in Packages', 'https://github.com/orafce/orafce#orafce---oracles-compatibility-functions-and-packages');
INSERT INTO releases VALUES ('orafce-pg15', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('orafce-pg16', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('orafce-pg15', '4.5.0-1',   'arm9, el9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('orafce-pg16', '4.5.0-1',   'arm9, el9', 1, '20230914', 'pg16', '', '');

INSERT INTO projects VALUES ('plv8', 'dev', 3, 0, 'hub', 0, 'https://github.com/plv8/plv8/tags',
  'plv8',   1, 'v8.png', 'Javascript Stored Procedures', 'https://github.com/plv8/plv8');
INSERT INTO releases VALUES ('plv8-pg15', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plv8-pg16', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plv8-pg15', '3.2.0-1', 'arm9, el9', 1, '20230829', 'pg15', '', '');
INSERT INTO versions VALUES ('plv8-pg16', '3.2.0-1', 'arm9, el9', 1, '20230927', 'pg16', '', '');

INSERT INTO projects VALUES ('pljava', 'dev', 3, 0, 'hub', 0, 'https://github.com/tada/pljava/releases', 
  'pljava', 1, 'pljava.png', 'Java Stored Procedures', 'https://github.com/tada/pljava');
INSERT INTO releases VALUES ('pljava-pg15', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pljava-pg16', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pljava-pg15', '1.6.4-1',  'arm9, el9',  0, '20230608', 'pg15', '', '');
INSERT INTO versions VALUES ('pljava-pg16', '1.6.4-1',  'arm9, el9',  0, '20230608', 'pg16', '', '');

INSERT INTO projects VALUES ('pldebugger', 'dev', 4, 0, 'hub', 0, 'https://github.com/EnterpriseDB/pldebugger/tags',
  'pldebugger', 1, 'debugger.png', 'Stored Procedure Debugger', 'https://github.com/EnterpriseDB/pldebugger');
INSERT INTO releases VALUES ('pldebugger-pg15', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pldebugger-pg15', '1.5-1',  'arm9, el9',  1, '20220720', 'pg15', '', '');

INSERT INTO projects VALUES ('plprofiler', 'dev', 3, 0, 'hub', 7, 'https://github.com/bigsql/plprofiler/tags',
  'plprofiler', 1, 'plprofiler.png', 'Stored Procedure Profiler', 'https://github.com/bigsql/plprofiler#plprofiler');
INSERT INTO releases VALUES ('plprofiler-pg15', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg16', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plprofiler-pg15', '4.2.4-1', 'arm9, el9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('plprofiler-pg16', '4.2.4-1', 'arm9, el9', 1, '20230914', 'pg16', '', '');
INSERT INTO versions VALUES ('plprofiler-pg15', '4.2.2-1', 'arm9, el9', 0, '20230731', 'pg15', '', '');
INSERT INTO versions VALUES ('plprofiler-pg16', '4.2.2-1', 'arm9, el9', 0, '20230731', 'pg16', '', '');

INSERT INTO projects VALUES ('postgrest', 'pge', 4, 3000, 'hub', 0, 'https://github.com/postgrest/postgrest/tags',
  'postgrest', 0, 'postgrest.png', 'a RESTful API', 'https://postgrest.org');
INSERT INTO releases VALUES ('postgrest', 9, 'postgrest', 'PostgREST', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('postgrest', '11.2.0-1', 'el9, arm9', 1, '20230927', '', '', 'https://postgrest.org');
INSERT INTO versions VALUES ('postgrest', '11.1.0-1', 'el9, arm9', 0, '20230629', '', '', 'https://postgrest.org');

INSERT INTO projects VALUES ('prompgexp', 'pge', 4, 9187, 'golang', 0, 'https://github.com/prometheus-community/postgres_exporter/tags',
  'prompgexp', 0, 'prometheus.png', 'Prometheus PG Exporter', 'https://github.com/prometheus-community/postgres_exporter');
INSERT INTO releases VALUES ('prompgexp', 9, 'prompgexp', 'Prometheus PG Exporter', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('prompgexp', '0.11.1', '', 0, '20220720', '', '', 'https://github.com/prometheus-community/postgres_exporter');

INSERT INTO projects VALUES ('audit', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgaudit/pgaudit/releases',
  'audit', 1, 'audit.png', 'Audit Logging', 'https://github.com/pgaudit/pgaudit');
INSERT INTO releases VALUES ('audit-pg15', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('audit-pg16', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('audit-pg15', '1.7.0-1', 'arm9, el9', 1, '20221013', 'pg15', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.7.0');
INSERT INTO versions VALUES ('audit-pg16', '16.0-1', 'arm9, el9', 1, '20230914', 'pg16', '', 'https://github.com/pgaudit/pgaudit/releases/tag/16.0');

INSERT INTO projects VALUES ('hintplan', 'ext', 4, 0, 'hub', 0, 'https://github.com/ossc-db/pg_hint_plan/tags',
  'hintplan', 1, 'hintplan.png', 'Execution Plan Hints', 'https://github.com/ossc-db/pg_hint_plan');
INSERT INTO releases VALUES ('hintplan-pg15', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hintplan-pg16', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hintplan-pg15', '1.5.1-1', 'arm9, el9', 1, '20230927', 'pg15', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.5.1');
INSERT INTO versions VALUES ('hintplan-pg16', '1.6.0-1', 'arm9, el9', 1, '20230927', 'pg16', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.6.0');

INSERT INTO projects VALUES ('readonly', 'ext', 4, 0, 'hub',0, 'https://github.com/pgedge/readonly/tags',
  'readonly', 1, 'readonly.png', 'Support READ-ONLY Databases', 'https://github.com/pgedge/readonly');
INSERT INTO releases VALUES ('readonly-pg15', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('readonly-pg15', '1.1.0-1', 'el9, arm9', 1, '20230402', 'pg15', '', '');

INSERT INTO projects VALUES ('timescaledb', 'ext', 4, 0, 'hub',0, 'https://github.com/timescale/timescaledb/releases',
  'timescaledb', 1, 'timescaledb.png', 'Timeseries Extension', 'https://github.com/timescaledb/timescaledb');
INSERT INTO releases VALUES ('timescaledb-pg15', 10, 'timescaledb', 'TimescaleDB', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('timescaledb-pg15', '2.11.2-1', 'el9, arm9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('timescaledb-pg15', '2.11.0-1', 'el9, arm9', 0, '20230524', 'pg15', '', '');

INSERT INTO projects VALUES ('curl', 'ext', 4, 0, 'hub',0, 'https://github.com/pg_curl/pg_curl/releases',
  'curl', 1, 'curl.png', 'Invoke JSON Services', 'https://github.com/pg_curl/pg_curl');
INSERT INTO releases VALUES ('curl-pg15', 10, 'curl', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('curl-pg16', 10, 'curl', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('curl-pg15', '2.1.1-1',  'el9, arm9', 1, '20230630', 'pg15', '', '');
INSERT INTO versions VALUES ('curl-pg16', '2.1.1-1',  'el9, arm9', 1, '20230630', 'pg16', '', '');
INSERT INTO versions VALUES ('curl-pg15', '1.0.27-1', 'el9, arm9', 0, '20230215', 'pg15', '', '');

INSERT INTO projects VALUES ('cron', 'ext', 4, 0, 'hub',0, 'https://github.com/citusdata/pg_cron/releases',
  'cron', 1, 'cron.png', 'Background Job Scheduler', 'https://github.com/citusdata/pg_cron');
INSERT INTO releases VALUES ('cron-pg15', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('cron-pg16', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('cron-pg15', '1.6.0-1', 'el9, arm9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('cron-pg16', '1.6.0-1', 'el9, arm9', 1, '20230914', 'pg16', '', '');
INSERT INTO versions VALUES ('cron-pg15', '1.5.2-1', 'el9, arm9', 0, '20230422', 'pg15', '', '');

INSERT INTO projects VALUES ('vector', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/vector/tags',
  'vector', 1, 'vector.png', 'Vector & Embeddings', 'https://github.com/pgedge/vector/#vector');
INSERT INTO releases VALUES ('vector-pg15', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('vector-pg16', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('vector-pg15', '0.5.0-1', 'el9, arm9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.5.0-1', 'el9, arm9', 1, '20230914', 'pg16', '', '');
INSERT INTO versions VALUES ('vector-pg15', '0.4.4-1', 'el9, arm9', 0, '20230731', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.4.4-1', 'el9, arm9', 0, '20230731', 'pg16', '', '');

INSERT INTO projects VALUES ('spock', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/spock/tags',
  'spock', 1, 'spock.png', 'Logical & Multi-Master Replication', 'https://github.com/pgedge/spock/#spock');
INSERT INTO releases VALUES ('spock31-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock31-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('spock31-pg15', '3.1.7-1', 'el9, arm9', 1, '20230927', 'pg15', '', '');
INSERT INTO versions VALUES ('spock31-pg16', '3.1.7-1', 'el9, arm9', 1, '20230927', 'pg16', '', '');
INSERT INTO versions VALUES ('spock31-pg15', '3.1.6-1', 'el9, arm9', 0, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('spock31-pg16', '3.1.6-1', 'el9, arm9', 0, '20230914', 'pg16', '', '');
INSERT INTO versions VALUES ('spock31-pg15', '3.1.5-1', 'el9, arm9', 0, '20230829', 'pg15', '', '');
INSERT INTO versions VALUES ('spock31-pg16', '3.1.5-1', 'el9, arm9', 0, '20230829', 'pg16', '', '');

INSERT INTO releases VALUES ('spock32-pg17', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('spock32-pg17', '3.2dev2-1', 'el9', 1, '20230928', 'pg17', '', '');

INSERT INTO projects VALUES ('pglogical', 'ext', 4, 0, 'hub', 1, 'https://github.com/2ndQuadrant/pglogical/releases',
  'pglogical', 1, 'spock.png', 'Logical Replication', 'https://github.com/2ndQuadrant/pglogical');
INSERT INTO releases VALUES ('pglogical-pg15', 4, 'pglogical', 'pgLogical', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pglogical-pg15', '2.4.3-1',  'arm9, el9', 1, '20230629', 'pg15', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_3');

INSERT INTO projects VALUES ('postgis', 'ext', 4, 1, 'hub', 3, 'http://postgis.net/source',
  'postgis', 1, 'postgis.png', 'Spatial Extensions', 'http://postgis.net');
INSERT INTO releases VALUES ('postgis-pg15', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO releases VALUES ('postgis-pg16', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('postgis-pg15', '3.4.0-1', 'el9, arm9', 1, '20230914', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.0/NEWS');
INSERT INTO versions VALUES ('postgis-pg16', '3.4.0-1', 'el9, arm9', 1, '20230914', 'pg16', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.0/NEWS');
INSERT INTO versions VALUES ('postgis-pg15', '3.3.4-1', 'el9, arm9', 0, '20230731', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.3.4/NEWS');

INSERT INTO projects VALUES ('pgadmin4', 'app', 3, 80, '', 1, 'https://www.pgadmin.org/news/',
  'pgadmin4', 0, 'pgadmin.png', 'PostgreSQL Tools', 'https://pgadmin.org');
INSERT INTO releases VALUES ('pgadmin4', 2, 'pgadmin4', 'pgAdmin 4', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('pgadmin4', '7.5', '', 0, '20230727', '', '', '');

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
INSERT INTO releases VALUES ('partman-pg16', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('partman-pg15', '4.7.4-1',  'arm9, el9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('partman-pg16', '4.7.4-1',  'arm9, el9', 1, '20230914', 'pg16', '', '');
INSERT INTO versions VALUES ('partman-pg15', '4.7.3-1',  'arm9, el9', 0, '20220418', 'pg15', '', '');

INSERT INTO projects VALUES ('hypopg', 'ext', 4, 0, 'hub', 8, 'https://github.com/HypoPG/hypopg/releases',
  'hypopg', 1, 'whatif.png', 'Hypothetical Indexes', 'https://hypopg.readthedocs.io/en/latest/');
INSERT INTO releases VALUES ('hypopg-pg15', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hypopg-pg16', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hypopg-pg15', '1.4.0-1',  'arm9, el9', 1, '20230608', 'pg15', '', '');
INSERT INTO versions VALUES ('hypopg-pg16', '1.4.0-1',  'arm9, el9', 1, '20230608', 'pg16', '', '');

INSERT INTO projects VALUES ('badger', 'app', 4, 0, 'hub', 6, 'https://github.com/darold/pgbadger/releases',
  'badger', 0, 'badger.png', 'Performance Reporting', 'https://pgbadger.darold.net');
INSERT INTO releases VALUES ('badger', 101, 'badger','pgBadger','', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('badger', '11.8', '', 0, '20220408', '', '', '');

INSERT INTO projects VALUES ('pgedge', 'pge', 0, 0, 'hub', 3, 'http://pgedge.org',
  'pgedge',  0, 'pgedge.png', 'Multi-Active Global Postgres Clusters', 'http://pgedge.com');
INSERT INTO releases VALUES ('pgedge', 1, 'pgedge',  'pgEdge', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('pgedge', '2-5',   '', 1, '20230927', '', '', '');
INSERT INTO versions VALUES ('pgedge', '2-4',   '', 0, '20230914', '', '', '');
INSERT INTO versions VALUES ('pgedge', '2-3',   '', 0, '20230829', '', '', '');

INSERT INTO projects VALUES ('nclibs', 'pge', 0, 0, 'hub', 3, 'https://github.com/pgedge',
  'nclibs',  0, 'nclibs.png', 'nclibs', 'https://github.com/pgedge');
INSERT INTO releases VALUES ('nclibs', 2, 'nclibs',  'nodectlLibs', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('nclibs', '1.0', '', 1, '20230715', '', '', '');

INSERT INTO projects VALUES ('pgcat', 'pge', 4, 5433, 'hub', 3, 'https://github.com/pgedge/pgcat/tags',
  'cat',  0, 'pgcat.png', 'Connection Pooler', 'https://github.com/pgedge/pgcat');
INSERT INTO releases VALUES ('pgcat', 2, 'pgcat',  'pgCat', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('pgcat', '1.1.1', 'el9, arm9', 1, '20230829', '', '', '');
INSERT INTO versions VALUES ('pgcat', '1.0.0', 'el9, arm9', 0, '20230629', '', '', '');

INSERT INTO projects VALUES ('backrest', 'pge', 4, 0, 'hub', 3, 'http://pgbackrest.org',
  'backrest',  0, 'backrest.png', 'Backup & Restore', 'http://pgbackrest.org');
INSERT INTO releases VALUES ('backrest', 2, 'backrest',  'pgBackRest', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('backrest', '2.47-1', 'el9, arm9', 1, '20230803', '', 'EL', '');
INSERT INTO versions VALUES ('backrest', '2.46-1', 'el9, arm9', 0, '20230524', '', 'EL', '');

INSERT INTO projects VALUES ('patroni', 'app', 11, 0, '', 4, 'https://github.com/pgedge/patroni/tags',
  'patroni', 0, 'patroni.png', 'HA', 'https://github.com/pgedge/patroni');
INSERT INTO releases VALUES ('patroni', 1, 'patroni', 'Patroni', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('patroni', '3.1.0.1', '', 1, '20230829', '', 'EL9', '');

INSERT INTO projects VALUES ('etcd', 'app', 11, 0, 'hub', 4, 'https://github.com/etcd-io/etcd/tags',
  'etcd', 0, 'etcd.png', 'HA', 'https://github.com/etcd-io/etcd');
INSERT INTO releases VALUES ('etcd', 1, 'etcd', 'Etcd', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('etcd', '3.5.9', 'el9, arm9', 1, '20230810', '', 'EL9', '');

INSERT INTO projects VALUES ('ddlx', 'ext',     4, 0, 'hub', 0, 'https://github.com/lacanoid/pgddl/releases', 'ddlx',  1, 'ddlx.png', 'DDL Extractor', 'https://github.com/lacanoid/pgddl#ddl-extractor-functions--for-postgresql');
INSERT INTO releases VALUES ('ddlx-pg13', 2, 'ddlx', 'DDLeXtact', '', 'prod','',  0, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('ddlx-pg13', '0.17-1', 'amd', 1, '2.210911', 'pg13', '', '');

INSERT INTO projects VALUES ('multicorn2', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgsql-io/multicorn2/tags',
  'multicorn2', 1, 'multicorn.png', 'Python FDW Library', 'http://multicorn2.org');
INSERT INTO releases VALUES ('multicorn2-pg15', 1, 'multicorn2', 'Multicorn2', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('multicorn2-pg15', '2.4-1', 'arm, el8', 1, '20220909', 'pg15', '', '');


CREATE TABLE locations (
  location      TEXT     NOT NULL NOT NULL PRIMARY KEY,
  location_nm   TEXT     NOT NULL,
  country       TEXT     NOT NULL REFERENCES countries(country),
  state         TEXT,
  lattitude     FLOAT    NOT NULL,
  longitude     FLOAT    NOT NULL
);
INSERT INTO locations VALUES ('iad', 'Northern Virginia',  'us', 'va',  38.951944,  -77.448055);
INSERT INTO locations VALUES ('cmh', 'Ohio',               'us', 'oh',  39.995000,  -82.889166);
INSERT INTO locations VALUES ('pdt', 'Oregon',             'us', 'or',  45.694765, -118.843008);
INSERT INTO locations VALUES ('sfo', 'Northern California','us', 'ca',  37.621312, -122.378955);
INSERT INTO locations VALUES ('atl', 'Atlanta',            'us', 'ga',  33.640411,  -84.419853);
INSERT INTO locations VALUES ('bos', 'Boston',             'us', 'ma',  42.366978,  -71.022362);
INSERT INTO locations VALUES ('chi', 'Chicago',            'us', 'il',  41.978611,  -87.904724);
INSERT INTO locations VALUES ('dfw', 'Dallas',             'us', 'tx',  32.848152,  -96.851349);
INSERT INTO locations VALUES ('den', 'Denver',             'us', 'co',  39.856094, -104.673737);
INSERT INTO locations VALUES ('iah', 'Houston',            'us', 'tx',  36.942810, -109.707108);
INSERT INTO locations VALUES ('mci', 'Kansas City',        'us', 'mo',  39.297010,  -94.690370);
INSERT INTO locations VALUES ('lax', 'Los Angeles',        'us', 'ca',  33.942791, -118.410042);
INSERT INTO locations VALUES ('las', 'Las Vegas',          'us', 'nv',  36.086010, -115.153969);
INSERT INTO locations VALUES ('mia', 'Miami',              'us', 'fl',  25.795865,  -80.287045);
INSERT INTO locations VALUES ('msp', 'Minneapolis',        'us', 'mn',  44.884358,  -93.214075);
INSERT INTO locations VALUES ('jfk', 'New York City',      'us', 'ny',  40.641766,  -73.780968);
INSERT INTO locations VALUES ('phl', 'Philadelphia',       'us', 'pa',  39.874193,  -75.247245);
INSERT INTO locations VALUES ('phx', 'Phoenix',            'us', 'az',  33.437269, -112.007788);
INSERT INTO locations VALUES ('pdx', 'Portland',           'us', 'or',  45.587555, -122.593333);
INSERT INTO locations VALUES ('sea', 'Seattle',            'us', 'wa',  47.443546, -122.301659);
INSERT INTO locations VALUES ('slc', 'Salt Lake City',     'us', 'ut',  40.7899,    111.9791);
INSERT INTO locations VALUES ('dsm', 'Iowa',               'us', 'ia',  41.5341,     93.6588);
INSERT INTO locations VALUES ('chs', 'Charleston',         'us', 'sc',  32.8943,     80.0382);
INSERT INTO locations VALUES ('jac', 'Wyoming',            'us', 'wy',  43.6034,    110.7363);
INSERT INTO locations VALUES ('ric', 'Central Virginia',   'us', 'va',  37.5066,     77.3208);

INSERT INTO locations VALUES ('mtl', 'Montreal',           'ca', 'qb',  45.508888,  -73.561668);
INSERT INTO locations VALUES ('yyz', 'Toronto',            'ca', 'on',  43.6777,     79.6248);

INSERT INTO locations VALUES ('gru', 'Sao Paulo',          'br', '',   -23.533773,  -46.625290);
INSERT INTO locations VALUES ('dub', 'Dublin',             'ir', '',    53.426448,   -6.249910);
INSERT INTO locations VALUES ('lhr', 'London',             'gb', '',    51.458881,   -0.470008);
INSERT INTO locations VALUES ('fra', 'Frankfurt',          'de', '',    50.037933,    8.562152);
INSERT INTO locations VALUES ('arn', 'Stockholm',          'se', '',    59.649762,   17.923781);
INSERT INTO locations VALUES ('cdg', 'Paris',              'fr', '',    49.009724,    2.547778);
INSERT INTO locations VALUES ('mxp', 'Milan',              'it', '',    45.628611,    8.723611);
INSERT INTO locations VALUES ('bah', 'Bahrain',            'bh', '',    26.269712,   50.625987);
INSERT INTO locations VALUES ('auh', 'UAE',                'ae', '',    24.432928,   54.644539);
INSERT INTO locations VALUES ('syd', 'Sydney',             'au', '',   -33.939922,  151.175276);
INSERT INTO locations VALUES ('cpt', 'Cape Town',          'za', '',   -33.972555,   18.601944);
INSERT INTO locations VALUES ('nrt', 'Tokyo',              'jp', '',    35.771987,  140.392855);
INSERT INTO locations VALUES ('itm', 'Osaka',              'jp', '',    34.433855,  135.226333);
INSERT INTO locations VALUES ('hkg', 'Hong Kong',          'hk', '',    22.308046,  113.918480);
INSERT INTO locations VALUES ('icn', 'Seoul',              'kr', '',    37.460191,  126.440696);
INSERT INTO locations VALUES ('sin', 'Singapore',          'sg', '',     1.420181,  103.864555);
INSERT INTO locations VALUES ('bom', 'Mumbai',             'in', '',    19.090176,   72.868739);
INSERT INTO locations VALUES ('yys', 'Calgary',            'ca', '',    51.1215,   -114.0078);
INSERT INTO locations VALUES ('mad', 'Madrid',             'es', '',    40.4840,     -3.5680);
INSERT INTO locations VALUES ('zrh', 'Zurich',             'se', '',    47.4515,      8.5646);
INSERT INTO locations VALUES ('akl', 'Auckland',           'nz', '',   -36.9993,    174.7879);
INSERT INTO locations VALUES ('hyd', 'Hyderabad',          'in', '',    17.2403,     78.4294);
INSERT INTO locations VALUES ('cgk', 'Jakarta',            'id', '',    -6.1256,    106.6558);
INSERT INTO locations VALUES ('mel', 'Melbourne',          'au', '',   -37.6637,    144.8448);
INSERT INTO locations VALUES ('pek', 'Beijing',            'cn', '',    40.0725,    116.5974);
INSERT INTO locations VALUES ('csx', 'Changsha',           'cn', '',    28.1913,    113.2192);
INSERT INTO locations VALUES ('tlv', 'Tel Aviv',           'il', '',    32.0055,     34.8854);
INSERT INTO locations VALUES ('bru', 'Brussels',           'be', '',    50.9010,      4.4856);
INSERT INTO locations VALUES ('ams', 'Amsterdam',          'nl', '',    52.3105,      4.7683);
INSERT INTO locations VALUES ('hel', 'Helsinki',           'fl', '',    60.3183,     24.9497);
INSERT INTO locations VALUES ('tpe', 'Taiwan',             'tw', '',    25.0797,    121.2342);
INSERT INTO locations VALUES ('scl', 'Santiago',           'cl', '',    33.3898,     70.7945);
INSERT INTO locations VALUES ('waw', 'Warsaw',             'pl', '',    52.1672,     20.9679);
INSERT INTO locations VALUES ('del', 'Delhi',              'in', '',    28.5562,     77.1000);
INSERT INTO locations VALUES ('jnb', 'Johannesburg',       'za', '',    26.1367,     28.2411);
INSERT INTO locations VALUES ('cwl', 'Cardiff',            'uk', '',    51.3985,      3.3397);
INSERT INTO locations VALUES ('osl', 'Oslo',               'no', '',    60.1976,     11.0004);
INSERT INTO locations VALUES ('doh', 'Doha',               'qa', '',    25.2609,     51.6138);
INSERT INTO locations VALUES ('pnq', 'Pune',               'in', '',    18.5793,     73.9089);
INSERT INTO locations VALUES ('maa', 'Chennai',            'in', '',    12.9941,     80.1707);
INSERT INTO locations VALUES ('pvg', 'Shanghai',           'cn', '',    31.1443,    121.8083);
INSERT INTO locations VALUES ('cbr', 'Canberra',           'au', '',    35.3052,    149.1934);

