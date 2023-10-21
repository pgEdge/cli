DROP VIEW  IF EXISTS v_versions;

DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS releases;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS categories;


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
  SELECT p.image_file, r.component, r.project, r.stage, r.disp_name as rel_name,
         v.version, p.sources_url, p.project_url, v.platform, 
         v.is_current, v.release_date as rel_date, p.description as proj_desc, 
         r.description as rel_desc, v.pre_reqs, r.license, p.depends, 
         r.is_available, v.release_notes as rel_notes
    FROM projects p, releases r, versions v
   WHERE p.project = r.project
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
INSERT INTO versions VALUES ('hub', '24.003', '',  1, '20231028', '', '', '');
INSERT INTO versions VALUES ('hub', '24.002', '',  0, '20231021', '', '', '');
INSERT INTO versions VALUES ('hub', '24.001', '',  0, '20231017', '', '', '');
INSERT INTO versions VALUES ('hub', '23.134', '',  0, '20231013', '', '', '');

-- ##
INSERT INTO projects VALUES ('pg', 'pge', 1, 5432, 'hub', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org');

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
INSERT INTO versions VALUES ('pg15', '15.4-3',  'el9',                 1, '20231021','', '', '');
INSERT INTO versions VALUES ('pg15', '15.4-2',  'el8, el9, arm9',      0, '20230829','', '', '');

INSERT INTO releases VALUES ('pg16', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/16/release-16.html>2023!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg16', '16.0-2',    'el9',       1, '20231021','', '', '');
INSERT INTO versions VALUES ('pg16', '16.0-1',    'el9, arm9', 0, '20230914','', '', '');

INSERT INTO releases VALUES ('pg17', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/17/release-17.html>2024!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg17', '17devel-2', 'el9', 1, '20231021','', '', '');
INSERT INTO versions VALUES ('pg17', '17devel-1', 'el9', 0, '20230927','', '', '');

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

INSERT INTO projects VALUES ('foslots', 'ext', 4, 0, 'hub',0, 'https://github.com/pgedge/foslots/tags',
  'foslots', 1, 'foslots.png', 'Failover Slots', 'https://github.com/pgedge/foslots');
INSERT INTO releases VALUES ('foslots-pg15', 10, 'foslots', 'FO Slots', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('foslots-pg16', 10, 'foslots', 'FO Slots', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('foslots-pg15', '1a-1', 'el9, arm9', 1, '20230929', 'pg15', '', '');
INSERT INTO versions VALUES ('foslots-pg16', '1a-1', 'el9, arm9', 1, '20230929', 'pg16', '', '');

INSERT INTO projects VALUES ('readonly', 'ext', 4, 0, 'hub',0, 'https://github.com/pgedge/readonly/tags',
  'readonly', 1, 'readonly.png', 'Support READ-ONLY Databases', 'https://github.com/pgedge/readonly');
INSERT INTO releases VALUES ('readonly-pg15', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('readonly-pg16', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('readonly-pg15', '1.1.0-1', 'el9, arm9', 1, '20230929', 'pg15', '', '');
INSERT INTO versions VALUES ('readonly-pg16', '1.1.0-1', 'el9, arm9', 1, '20230929', 'pg16', '', '');

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

INSERT INTO projects VALUES ('spock', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/spock/tags',
  'spock', 1, 'spock.png', 'Logical & Multi-Master Replication', 'https://github.com/pgedge/spock/#spock');
INSERT INTO releases VALUES ('spock31-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock31-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('spock31-pg15', '3.1.7-1', 'el9, arm9', 1, '20230927', 'pg15', '', '');
INSERT INTO versions VALUES ('spock31-pg16', '3.1.7-1', 'el9, arm9', 1, '20230927', 'pg16', '', '');

INSERT INTO projects VALUES ('snowflake', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/snowflake/tags',
  'snowflake', 1, 'snowflake.png', 'Snowflake Sequences', 'https://github.com/pgedge/snowflake/');
INSERT INTO releases VALUES ('snowflake-pg15', 4, 'snowflake', 'Snowflake', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg16', 4, 'snowflake', 'Snowflake', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg17', 4, 'snowflake', 'Snowflake', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('snowflake-pg15', '1.1-1', 'el9', 1, '20231017', 'pg15', '', '');
INSERT INTO versions VALUES ('snowflake-pg16', '1.1-1', 'el9', 1, '20231017', 'pg16', '', '');
INSERT INTO versions VALUES ('snowflake-pg17', '1.1-1', 'el9', 1, '20231017', 'pg17', '', '');

INSERT INTO releases VALUES ('spock32-pg15', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock32-pg16', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock32-pg17', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('spock32-pg17', '3.2dev5-1', 'el9', 1, '20231021', 'pg17', '', '');

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
INSERT INTO releases VALUES ('pgedge', 1, 'pgedge',  'pgEdge', '', 'prod', '', 1, 'pgEdge Platform', '', '');
INSERT INTO versions VALUES ('pgedge', '2-6',   '', 1, '20231017', '', '', '');
INSERT INTO versions VALUES ('pgedge', '2-5',   '', 0, '20230927', '', '', '');
INSERT INTO versions VALUES ('pgedge', '2-4',   '', 0, '20230914', '', '', '');

INSERT INTO projects VALUES ('nclibs', 'pge', 0, 0, 'hub', 3, 'https://github.com/pgedge/nodectl',
  'nclibs',  0, 'nclibs.png', 'nclibs', 'https://github.com/pgedge/nodectl');
INSERT INTO releases VALUES ('nclibs', 2, 'nclibs',  'nodectl Libs', '', 'test', '', 1, '', '', '');
INSERT INTO versions VALUES ('nclibs', '1.0', '', 1, '20231021', '', '', '');

INSERT INTO projects VALUES ('pgcat', 'pge', 4, 5433, 'hub', 3, 'https://github.com/pgedge/pgcat/tags',
  'cat',  0, 'pgcat.png', 'Connection Pooler', 'https://github.com/pgedge/pgcat');
INSERT INTO releases VALUES ('pgcat', 2, 'pgcat',  'pgCat', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('pgcat', '1.1.1', 'el9, arm9', 1, '20230829', '', '', '');
INSERT INTO versions VALUES ('pgcat', '1.0.0', 'el9, arm9', 0, '20230629', '', '', '');

INSERT INTO projects VALUES ('backrest', 'pge', 4, 0, 'hub', 3, 'http://pgbackrest.org',
  'backrest',  0, 'backrest.png', 'Backup & Restore', 'http://pgbackrest.org');
INSERT INTO releases VALUES ('backrest', 2, 'backrest',  'pgBackRest', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('backrest', '2.47-1', 'el9, arm9', 1, '20230803', '', 'EL', '');
INSERT INTO versions VALUES ('backrest', '2.46-1', 'el9, arm9', 0, '20230524', '', 'EL', '');

INSERT INTO projects VALUES ('staz', 'app', 11, 0, '', 4, 'https://github.com/pgedge/staz/tags',
  'staz', 0, 'patroni.png', 'HA', 'https://github.com/pgedge/staz');
INSERT INTO releases VALUES ('staz', 1, 'staz', 'STAZ', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('staz', '3.1.2.2', '', 1, '20231021', '', 'EL9', '');

INSERT INTO projects VALUES ('etcd', 'app', 11, 0, 'hub', 4, 'https://github.com/etcd-io/etcd/tags',
  'etcd', 0, 'etcd.png', 'HA', 'https://github.com/etcd-io/etcd');
INSERT INTO releases VALUES ('etcd', 1, 'etcd', 'Etcd', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('etcd', '3.5.9', 'el9, arm9', 1, '20231013', '', 'EL9', '');

INSERT INTO projects VALUES ('ddlx', 'ext',     4, 0, 'hub', 0, 'https://github.com/lacanoid/pgddl/releases', 'ddlx',  1, 'ddlx.png', 'DDL Extractor', 'https://github.com/lacanoid/pgddl#ddl-extractor-functions--for-postgresql');
INSERT INTO releases VALUES ('ddlx-pg13', 2, 'ddlx', 'DDLeXtact', '', 'prod','',  0, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('ddlx-pg13', '0.17-1', 'amd', 1, '2.210911', 'pg13', '', '');

INSERT INTO projects VALUES ('multicorn2', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgsql-io/multicorn2/tags',
  'multicorn2', 1, 'multicorn.png', 'Python FDW Library', 'http://multicorn2.org');
INSERT INTO releases VALUES ('multicorn2-pg15', 1, 'multicorn2', 'Multicorn2', '', 'test','',  1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('multicorn2-pg15', '2.4-1', 'arm, el8', 1, '20220909', 'pg15', '', '');

