DROP VIEW  IF EXISTS v_versions;

DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS extensions;
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


CREATE TABLE extensions (
  component      TEXT NOT NULL PRIMARY KEY,
  extension_name TEXT NOT NULL,
  is_preload     INTEGER NOT NULL,
  preload_name   TEXT NOT NULL,
  default_conf   TEXT NOT NULL
);
INSERT INTO extensions VALUES ('spock33', 'spock', 1, 'spock',
  'wal_level=logical | max_worker_processes=12 | max_replication_slots=16 |
   max_wal_senders=16 | hot_standby_feedback=on | wal_sender_timeout=5s |
   track_commit_timestamp=on | spock.conflict_resolution=last_update_wins | 
   spock.save_resolutions=on');
INSERT INTO extensions VALUES ('spock40', 'spock', 1, 'spock',
  'wal_level=logical | max_worker_processes=12 | max_replication_slots=16 |
   max_wal_senders=16 | hot_standby_feedback=on | wal_sender_timeout=5s |
   track_commit_timestamp=on | spock.conflict_resolution=last_update_wins | 
   spock.save_resolutions=on');
INSERT INTO extensions VALUES ('lolor',     'lolor',     0, '',          '');
INSERT INTO extensions VALUES ('postgis',   'postgis',   1, 'postgis-3', '');
INSERT INTO extensions VALUES ('orafce',    'orafce',    1, 'orafce',    '');
INSERT INTO extensions VALUES ('snowflake', 'snowflake', 1, 'snowflake', '');
INSERT INTO extensions VALUES ('foslots',   'foslots',   0, '',          '');
  


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
INSERT INTO categories VALUES (1,  10, 'Postgres', 'Postgres');
INSERT INTO categories VALUES (11, 30, 'Applications', 'Applications');
INSERT INTO categories VALUES (10, 15, 'Streaming Change Data Capture', 'CDC');
INSERT INTO categories VALUES (2,  12, 'Legacy RDBMS', 'Legacy');
INSERT INTO categories VALUES (6,  20, 'Oracle Migration & Compatibility', 'OracleMig');
INSERT INTO categories VALUES (4,  11, 'Extensions', 'Extensions');
INSERT INTO categories VALUES (5,  25, 'Data Integration', 'Integration');
INSERT INTO categories VALUES (3,  80, 'Database Developers', 'Developers');
INSERT INTO categories VALUES (9,  87, 'Management & Monitoring', 'Manage/Monitor');

-- ## HUB ################################
INSERT INTO projects VALUES ('hub', 'app', 0, 0, 'hub', 0, 'https://github.com/pgedge/cli','',0,'','','');
INSERT INTO releases VALUES ('hub', 1, 'hub', '', '', 'hidden', '', 1, '', '', '');
INSERT INTO versions VALUES ('hub', '24.4.5',  '',  1, '20240410', '', '', '');
INSERT INTO versions VALUES ('hub', '24.4.4',  '',  0, '20240405', '', '', '');
INSERT INTO versions VALUES ('hub', '24.4.3',  '',  0, '20240402', '', '', '');
INSERT INTO versions VALUES ('hub', '24.4.2',  '',  0, '20240401', '', '', '');
INSERT INTO versions VALUES ('hub', '24.3.2',  '',  0, '20240317', '', '', '');
INSERT INTO versions VALUES ('hub', '24.1.3',  '',  0, '20231205', '', '', '');

-- ##
INSERT INTO projects VALUES ('pg', 'pge', 1, 5432, 'hub', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org');

INSERT INTO releases VALUES ('pg12', 3, 'pg', 'PostgreSQL', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/12/release-12.html>2019</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg12', '12.18-1', 'el8', 1, '20240208', '', '', '');
INSERT INTO versions VALUES ('pg12', '12.17-1', 'el8', 0, '20231109', '', '', '');

INSERT INTO releases VALUES ('pg13', 2, 'pg', '', '', 'prod',
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/13/release-13.html>2020</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg13', '13.14-1', 'el8', 1, '20240208','', '', '');
INSERT INTO versions VALUES ('pg13', '13.13-1', 'el8', 0, '20231109','', '', '');

INSERT INTO releases VALUES ('pg14', 1, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/14/release-14.html>2021</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg14', '14.11-1', 'el8, el9, arm9', 1, '20240208', '','','');
INSERT INTO versions VALUES ('pg14', '14.10-2', 'el8, el9, arm9', 0, '20240108', '','','');

INSERT INTO releases VALUES ('pg15', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/15/release-15.html>2022</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg15', '15.6-4',  'el8, el9, arm9', 1, '20240317','', '', '');
INSERT INTO versions VALUES ('pg15', '15.6-3',  'el8, el9, arm9', 0, '20240301','', '', '');
INSERT INTO versions VALUES ('pg15', '15.6-1',  'el8, el9, arm9', 0, '20240208','', '', '');
INSERT INTO versions VALUES ('pg15', '15.5-1',  'el8, el9, arm9', 0, '20231109','', '', '');

INSERT INTO releases VALUES ('pg16', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/16/release-16.html>2023!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg16', '16.2-4',  'el8, el9, arm9, osx', 1, '20240317','', '', '');
INSERT INTO versions VALUES ('pg16', '16.2-3',  'el8, el9, arm9, osx', 0, '20240301','', '', '');
INSERT INTO versions VALUES ('pg16', '16.2-2',  'el8, el9, arm9', 0, '20240212','', '', '');
INSERT INTO versions VALUES ('pg16', '16.2-1',  'el8, el9, arm9', 0, '20240208','', '', '');
INSERT INTO versions VALUES ('pg16', '16.1-1',  'el8, el9, arm9', 0, '20231109','', '', '');

INSERT INTO releases VALUES ('pg17', 2, 'pg', '', '', 'test', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/17/release-17.html>2024!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg17', '17devel-1',  'el9', 1, '20240108','', '', '');

INSERT INTO projects VALUES ('orafce', 'ext', 4, 0, 'hub', 0, 'https://github.com/orafce/orafce/releases',
  'orafce', 1, 'larry.png', 'Ora Built-in Packages', 'https://github.com/orafce/orafce#orafce---oracles-compatibility-functions-and-packages');
INSERT INTO releases VALUES ('orafce-pg15', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('orafce-pg16', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('orafce-pg15', '4.9.2-1',   'arm9, el9', 1, '20240212', 'pg15', '', '');
INSERT INTO versions VALUES ('orafce-pg16', '4.9.2-1',   'arm9, el9', 1, '20240212', 'pg16', '', '');
INSERT INTO versions VALUES ('orafce-pg15', '4.5.0-1',   'arm9, el9', 0, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('orafce-pg16', '4.5.0-1',   'arm9, el9', 0, '20230914', 'pg16', '', '');

INSERT INTO projects VALUES ('plv8', 'dev', 4, 0, 'hub', 0, 'https://github.com/plv8/plv8/tags',
  'plv8',   1, 'v8.png', 'Javascript Stored Procedures', 'https://github.com/plv8/plv8');
INSERT INTO releases VALUES ('plv8-pg16', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plv8-pg16', '3.2.2-1', 'arm9, el9', 1, '20240214', 'pg16', '', '');

INSERT INTO projects VALUES ('pljava', 'dev', 4, 0, 'hub', 0, 'https://github.com/tada/pljava/releases', 
  'pljava', 1, 'pljava.png', 'Java Stored Procedures', 'https://github.com/tada/pljava');
INSERT INTO releases VALUES ('pljava-pg15', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pljava-pg16', 7, 'pljava', 'PL/Java', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pljava-pg15', '1.6.4-1',  'arm9, el9',  0, '20230608', 'pg15', '', '');
INSERT INTO versions VALUES ('pljava-pg16', '1.6.4-1',  'arm9, el9',  0, '20230608', 'pg16', '', '');

INSERT INTO projects VALUES ('pldebugger', 'dev', 4, 0, 'hub', 0, 'https://github.com/EnterpriseDB/pldebugger/tags',
  'pldebugger', 1, 'debugger.png', 'Stored Procedure Debugger', 'https://github.com/EnterpriseDB/pldebugger');
INSERT INTO releases VALUES ('pldebugger-pg15', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pldebugger-pg16', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pldebugger-pg15', '1.6-1',  'arm9, el9',  1, '20231112', 'pg15', '', '');
INSERT INTO versions VALUES ('pldebugger-pg16', '1.6-1',  'arm9, el9',  1, '20231112', 'pg16', '', '');

INSERT INTO projects VALUES ('plprofiler', 'dev', 4, 0, 'hub', 7, 'https://github.com/bigsql/plprofiler/tags',
  'plprofiler', 1, 'plprofiler.png', 'Stored Procedure Profiler', 'https://github.com/bigsql/plprofiler#plprofiler');
INSERT INTO releases VALUES ('plprofiler-pg15', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg16', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('plprofiler-pg15', '4.2.4-1', 'arm9, el9', 1, '20230914', 'pg15', '', '');
INSERT INTO versions VALUES ('plprofiler-pg16', '4.2.4-1', 'arm9, el9', 1, '20230914', 'pg16', '', '');

INSERT INTO projects VALUES ('prest', 'pge', 11, 3000, 'hub', 0, 'https://github.com/prest/prest/release',
  'prest', 0, 'prest.png', 'a RESTful API', 'https://prest.org');
INSERT INTO releases VALUES ('prest', 9, 'prest', 'pREST', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('prest', '1.4.2', 'el8, el9, arm9', 1, '20240221', '', '', '');

INSERT INTO projects VALUES ('postgrest', 'pge', 11, 3000, 'hub', 0, 'https://github.com/postgrest/postgrest/tags',
  'postgrest', 0, 'postgrest.png', 'a RESTful API', 'https://postgrest.org');
INSERT INTO releases VALUES ('postgrest', 9, 'postgrest', 'PostgREST', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('postgrest', '12.0.2-1', 'el9, arm9', 0, '20240212', '', 'EL9', 'https://postgrest.org');

INSERT INTO projects VALUES ('prompgexp', 'pge', 11, 9187, 'golang', 0, 'https://github.com/prometheus-community/postgres_exporter/tags',
  'prompgexp', 0, 'prometheus.png', 'Prometheus PG Exporter', 'https://github.com/prometheus-community/postgres_exporter');
INSERT INTO releases VALUES ('prompgexp', 9, 'prompgexp', 'Prometheus Postgres Exporter', '', 'prod', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('prompgexp', '0.15.0-1', 'el9, arm9', 1, '20240221', '', '', 'https://github.com/prometheus-community/postgres_exporter');

INSERT INTO projects VALUES ('audit', 'ext', 4, 0, 'hub', 0, 'https://github.com/pgaudit/pgaudit/releases',
  'audit', 1, 'audit.png', 'Audit Logging', 'https://github.com/pgaudit/pgaudit');
INSERT INTO releases VALUES ('audit-pg15', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('audit-pg16', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('audit-pg15', '1.7.0-1', 'arm9, el9', 1, '20230914', 'pg15', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.7.0');
INSERT INTO versions VALUES ('audit-pg16', '16.0-1',  'arm9, el9', 1, '20230914', 'pg16', '', 'https://github.com/pgaudit/pgaudit/releases/tag/16.0');

INSERT INTO projects VALUES ('wal2json', 'ext', 4, 0, 'hub', 0, 'https://github.com/eulerto/wal2json/tags',
  'wal2json', 1, 'wal2json.png', 'WAL to JSON for CDC', 'https://github.com/eulerto/wal2json');
INSERT INTO releases VALUES ('wal2json-pg15', 10, 'wal2json', 'wal2json', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('wal2json-pg16', 10, 'wal2json', 'wal2json', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('wal2json-pg15', '2.5.1-1', 'arm9, el9', 1, '20240221', 'pg15', '', 'https://github.com/eulerto/wal2json/tags');
INSERT INTO versions VALUES ('wal2json-pg16', '2.5.1-1', 'arm9, el9', 1, '20230221', 'pg16', '', 'https://github.com/eulerto/wal2json/tags');

INSERT INTO projects VALUES ('hintplan', 'ext', 4, 0, 'hub', 0, 'https://github.com/ossc-db/pg_hint_plan/tags',
  'hintplan', 1, 'hintplan.png', 'Execution Plan Hints', 'https://github.com/ossc-db/pg_hint_plan');
INSERT INTO releases VALUES ('hintplan-pg15', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hintplan-pg16', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('hintplan-pg15', '1.5.1-1', 'arm9, el9', 1, '20230927', 'pg15', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.5.1');
INSERT INTO versions VALUES ('hintplan-pg16', '1.6.0-1', 'arm9, el9', 1, '20230927', 'pg16', '', 'https://github.com/pghintplan/pghintplan/releases/tag/1.6.0');

INSERT INTO projects VALUES ('foslots', 'ext', 4, 0, 'hub',0, 'https://github.com/pgedge/foslots/tags',
  'foslots', 1, 'foslots.png', 'Failover Slots', 'https://github.com/pgedge/foslots');
INSERT INTO releases VALUES ('foslots-pg14', 10, 'foslots', 'FO Slots', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('foslots-pg15', 10, 'foslots', 'FO Slots', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('foslots-pg14', '1a-1', 'el8, el9, arm9', 1, '20240402', 'pg14', '', '');
INSERT INTO versions VALUES ('foslots-pg15', '1a-1', 'el8, el9, arm9', 1, '20240402', 'pg15', '', '');

INSERT INTO projects VALUES ('readonly', 'ext', 4, 0, 'hub',0, 'https://github.com/pgedge/readonly/tags',
  'readonly', 1, 'readonly.png', 'Support READ-ONLY Databases', 'https://github.com/pgedge/readonly');
INSERT INTO releases VALUES ('readonly-pg14', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('readonly-pg15', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('readonly-pg16', 10, 'readonly', 'pgReadOnly', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('readonly-pg14', '1.1.1-1', 'el8, el9, arm9', 1, '20240108', 'pg14', '', '');
INSERT INTO versions VALUES ('readonly-pg15', '1.1.1-1', 'el8, el9, arm9', 1, '20240108', 'pg15', '', '');
INSERT INTO versions VALUES ('readonly-pg16', '1.1.1-1', 'el8, el9, arm9', 1, '20240128', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('timescaledb', 'ext', 4, 0, 'hub',0, 'https://github.com/timescale/timescaledb/releases',
  'timescaledb', 1, 'timescaledb.png', 'Timeseries Extension', 'https://github.com/timescaledb/timescaledb');
INSERT INTO releases VALUES ('timescaledb-pg15', 10, 'timescaledb', 'TimescaleDB', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('timescaledb-pg16', 10, 'timescaledb', 'TimescaleDB', '', 'test', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('timescaledb-pg15', '2.13.1-1', 'el9, arm9', 1, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('timescaledb-pg16', '2.13.1-1', 'el9, arm9', 1, '20240130', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('curl', 'ext', 4, 0, 'hub',0, 'https://github.com/pg_curl/pg_curl/releases',
  'curl', 1, 'curl.png', 'Invoke JSON Services', 'https://github.com/pg_curl/pg_curl');
INSERT INTO releases VALUES ('curl-pg15', 10, 'curl', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('curl-pg16', 10, 'curl', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('curl-pg15', '2.2.2-1',  'el9, arm9', 1, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('curl-pg16', '2.2.2-1',  'el9, arm9', 1, '20240130', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('citus', 'pge', 4, 0, 'hub',0, 'https://github.com/citusdata/citus/releases',
  'citus', 1, 'citus.png', 'Sharded Postgres', 'https://github.com/citusdata/citus');
INSERT INTO releases VALUES ('citus-pg15', 10, 'citus', 'Citus', '', 'prod', '', 1, 'AGPLv3', '', '');
INSERT INTO releases VALUES ('citus-pg16', 10, 'citus', 'Citus', '', 'prod', '', 1, 'AGPLv3', '', '');

INSERT INTO versions VALUES ('citus-pg15', '12.1.2-1', 'el9, arm9', 1, '20240301', 'pg15', '', '');
INSERT INTO versions VALUES ('citus-pg16', '12.1.2-1', 'el9, arm9', 1, '20240301', 'pg16', '', '');

INSERT INTO versions VALUES ('citus-pg15', '12.1.1-1', 'el9, arm9', 0, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('citus-pg16', '12.1.1-1', 'el9, arm9', 0, '20240130', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('cron', 'ext', 4, 0, 'hub',0, 'https://github.com/citusdata/pg_cron/releases',
  'cron', 1, 'cron.png', 'Background Job Scheduler', 'https://github.com/citusdata/pg_cron');
INSERT INTO releases VALUES ('cron-pg15', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('cron-pg16', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('cron-pg15', '1.6.2-1', 'el9, arm9', 1, '20231112', 'pg15', '', '');
INSERT INTO versions VALUES ('cron-pg16', '1.6.2-1', 'el9, arm9', 1, '20231112', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('vector', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/vector/tags',
  'vector', 1, 'vector.png', 'Vector & Embeddings', 'https://github.com/pgedge/vector/#vector');
INSERT INTO releases VALUES ('vector-pg15', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('vector-pg16', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('vector-pg15', '0.7.0-1', 'el9, arm9', 1, '20240503', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.7.0-1', 'el9, arm9', 1, '20240503', 'pg16', '', '');

INSERT INTO versions VALUES ('vector-pg15', '0.6.2-1', 'el9, arm9', 0, '20240328', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.6.2-1', 'el9, arm9', 0, '20240328', 'pg16', '', '');

INSERT INTO versions VALUES ('vector-pg15', '0.6.1-1', 'el9, arm9', 0, '20240307', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.6.1-1', 'el9, arm9', 0, '20240307', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('snowflake', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/snowflake/tags',
  'snowflake', 1, 'snowflake.png', 'Snowflake Sequences', 'https://github.com/pgedge/snowflake/');
INSERT INTO releases VALUES ('snowflake-pg14', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg15', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg16', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('snowflake-pg14', '2.0-1', 'el8, el9, arm9',      1, '20240405', 'pg14', '', '');
INSERT INTO versions VALUES ('snowflake-pg15', '2.0-1', 'el8, el9, arm9',      1, '20240405', 'pg15', '', '');
INSERT INTO versions VALUES ('snowflake-pg16', '2.0-1', 'el8, el9, arm9, osx', 1, '20240405', 'pg16', '', '');

INSERT INTO versions VALUES ('snowflake-pg14', '1.2-1', 'el8, el9, arm9', 0, '20240302', 'pg14', '', '');
INSERT INTO versions VALUES ('snowflake-pg15', '1.2-1', 'el8, el9, arm9', 0, '20240302', 'pg15', '', '');
INSERT INTO versions VALUES ('snowflake-pg16', '1.2-1', 'el8, el9, arm9, osx', 0, '20240302', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('spock', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/spock/tags',
  'spock', 1, 'spock.png', 'Logical & Multi-Master Replication', 'https://github.com/pgedge/spock/#spock');
INSERT INTO releases VALUES ('spock32-pg14', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock32-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock32-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('spock32-pg14', '3.2.8-1', 'el8, el9, arm9', 0, '20240307', 'pg14', '', '');
INSERT INTO versions VALUES ('spock32-pg15', '3.2.8-1', 'el8, el9, arm9', 0, '20240307', 'pg15', '', '');
INSERT INTO versions VALUES ('spock32-pg16', '3.2.8-1', 'el8, el9, arm9, osx', 0, '20240307', 'pg16', '', '');

----------------------------------
INSERT INTO releases VALUES ('spock33-pg14', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock33-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock33-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('spock33-pg14', '3.3.3-1', 'el8, el9, arm9', 1, '20240502', 'pg14', '', '');
INSERT INTO versions VALUES ('spock33-pg15', '3.3.3-1', 'el8, el9, arm9', 1, '20240502', 'pg15', '', '');
INSERT INTO versions VALUES ('spock33-pg16', '3.3.3-1', 'el8, el9, arm9, osx', 1, '20240502', 'pg16', '', '');

INSERT INTO versions VALUES ('spock33-pg14', '3.3.2-1', 'el8, el9, arm9', 0, '20240410', 'pg14', '', '');
INSERT INTO versions VALUES ('spock33-pg15', '3.3.2-1', 'el8, el9, arm9', 0, '20240410', 'pg15', '', '');
INSERT INTO versions VALUES ('spock33-pg16', '3.3.2-1', 'el8, el9, arm9, osx', 0, '20240410', 'pg16', '', '');

INSERT INTO versions VALUES ('spock33-pg14', '3.3.1-1', 'el8, el9, arm9', 0, '20240317', 'pg14', '', '');
INSERT INTO versions VALUES ('spock33-pg15', '3.3.1-1', 'el8, el9, arm9', 0, '20240317', 'pg15', '', '');
INSERT INTO versions VALUES ('spock33-pg16', '3.3.1-1', 'el8, el9, arm9, osx', 0, '20240317', 'pg16', '', '');

----------------------------------
INSERT INTO releases VALUES ('spock40-pg15', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock40-pg16', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');

--INSERT INTO versions VALUES ('spock40-pg15', '4.0dev-1', 'el9, arm9', 1, '20240503', 'pg15', '', '');
INSERT INTO versions VALUES ('spock40-pg16', '4.0dev-1', 'el9, arm9', 1, '20240503', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('lolor', 'pge', 4, 0, 'hub', 1, 'https://github.com/pgedge/lolor/tags',
  'spock', 1, 'spock.png', 'Logical Replication of Large Objects', 'https://github.com/pgedge/lolor/#spock');
INSERT INTO releases VALUES ('lolor-pg16', 4, 'lolor', 'LgObjLOgicalRep', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO versions VALUES ('lolor-pg16', '1.0beta1-1', 'el9, arm9, el8', 1, '20240401', 'pg16', '', '');

----------------------------------
INSERT INTO projects VALUES ('pglogical', 'ext', 4, 0, 'hub', 1, 'https://github.com/2ndQuadrant/pglogical/releases',
  'pglogical', 1, 'spock.png', 'Logical Replication', 'https://github.com/2ndQuadrant/pglogical');
INSERT INTO releases VALUES ('pglogical-pg15', 4, 'pglogical', 'pgLogical', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pglogical-pg16', 4, 'pglogical', 'pgLogical', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pglogical-pg15', '2.4.4-1',  'arm9, el9', 1, '20231112', 'pg15', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_4');
INSERT INTO versions VALUES ('pglogical-pg16', '2.4.4-1',  'arm9, el9', 1, '20231112', 'pg16', '', 'https://github.com/2ndQuadrant/pglogical/releases/tag/REL2_4_4');

INSERT INTO projects VALUES ('postgis', 'ext', 4, 1, 'hub', 3, 'http://postgis.net/source',
  'postgis', 1, 'postgis.png', 'Spatial Extensions', 'http://postgis.net');
INSERT INTO releases VALUES ('postgis-pg15', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO releases VALUES ('postgis-pg16', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('postgis-pg15', '3.4.2-1', 'el9, arm9', 1, '20240307', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.2/NEWS');
INSERT INTO versions VALUES ('postgis-pg16', '3.4.2-1', 'el9, arm9', 1, '20240307', 'pg16', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.2/NEWS');
INSERT INTO versions VALUES ('postgis-pg15', '3.4.1-1', 'el9, arm9', 0, '20240130', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.1/NEWS');
INSERT INTO versions VALUES ('postgis-pg16', '3.4.1-1', 'el9, arm9', 0, '20240130', 'pg16', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.4.1/NEWS');

INSERT INTO projects VALUES ('pgadmin4', 'app', 11, 443, '', 1, 'https://www.pgadmin.org/news/',
  'pgadmin4', 0, 'pgadmin.png', 'PostgreSQL Tools', 'https://pgadmin.org');
INSERT INTO releases VALUES ('pgadmin4', 2, 'pgadmin4', 'pgAdmin 4', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pgadmin4', '8.x', '', 1, '20240108', '', '', '');
INSERT INTO versions VALUES ('pgadmin4', '7-1', '', 0, '20231107', '', '', '');

INSERT INTO projects VALUES ('partman', 'ext', 4, 0, 'hub', 4, 'https://github.com/pgpartman/pg_partman/tags',
  'partman', 1, 'partman.png', 'Partition Management', 'https://github.com/pgpartman/pg_partman#pg-partition-manager');
INSERT INTO releases VALUES ('partman-pg15', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('partman-pg16', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('partman-pg15', '5.0.1-1',  'arm9, el9', 1, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('partman-pg16', '5.0.1-1',  'arm9, el9', 1, '20240130', 'pg16', '', '');

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

INSERT INTO projects VALUES ('ctlibs', 'pge', 0, 0, 'hub', 3, 'https://github.com/pgedge/cli',
  'ctlibs',  0, 'ctlibs.png', 'ctlibs', 'https://github.com/pgedge/cli');
INSERT INTO releases VALUES ('ctlibs', 2, 'ctlibs',  'nodectl Libs', '', 'prod', '', 1, '', '', '');
INSERT INTO versions VALUES ('ctlibs', '1.2', '', 1, '20240130', '', '', '');

INSERT INTO projects VALUES ('pgcat', 'pge', 11, 5433, 'hub', 3, 'https://github.com/pgedge/pgcat/tags',
  'cat',  0, 'pgcat.png', 'Connection Pooler', 'https://github.com/pgedge/pgcat');
INSERT INTO releases VALUES ('pgcat', 2, 'pgcat',  'pgCat', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('pgcat', '1.1.1', 'el8, el9, arm9', 1, '20240108', '', '', '');

INSERT INTO projects VALUES ('backrest', 'pge', 11, 0, 'hub', 3, 'http://pgbackrest.org',
  'backrest',  0, 'backrest.png', 'Backup & Restore', 'http://pgbackrest.org');
INSERT INTO releases VALUES ('backrest', 2, 'backrest',  'pgBackRest', '', 'prod', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('backrest', '2.51-1', 'el8, el9, arm9', 1, '20240410', '', '', '');
INSERT INTO versions VALUES ('backrest', '2.50-3', 'el8, el9, arm9', 0, '20240317', '', '', '');

INSERT INTO projects VALUES ('firewalld', 'app', 11, 0, '', 4, 'https://firewalld.org',
  'firewalld', 0, 'firewalld.png', 'OS Firewall', 'https://github.com/firewalld/firewalld');
INSERT INTO releases VALUES ('firewalld', 1, 'firewalld', 'Firewalld', '', 'ent', '', 1, 'GPLv2', '', '');
INSERT INTO versions VALUES ('firewalld', '1.2', '', 1, '20231101', '', '', '');

INSERT INTO projects VALUES ('patroni', 'app', 11, 0, 'etcd', 4, 'https://github.com/pgedge/pgedge-patroni/release',
  'patroni', 0, 'patroni.png', 'HA', 'https://github.com/pgedge/pgedge-patroni');
INSERT INTO releases VALUES ('patroni', 1, 'patroni', 'pgEdge Patroni', '', 'ent', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('patroni', '3.2.2.1-1', '', 1, '20240401', '', '', '');
INSERT INTO versions VALUES ('patroni', '3.2.1-1', '', 0, '20240221', '', '', '');

INSERT INTO projects VALUES ('etcd', 'app', 11, 2379, 'hub', 4, 'https://github.com/etcd-io/etcd/tags',
  'etcd', 0, 'etcd.png', 'HA', 'https://github.com/etcd-io/etcd');
INSERT INTO releases VALUES ('etcd', 1, 'etcd', 'Etcd', '', 'ent', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('etcd', '3.5.12-2', 'el8, el9, arm9', 1, '20240328', '', '', '');
INSERT INTO versions VALUES ('etcd', '3.5.12',   'el8, el9, arm9', 0, '20240221', '', '', '');

-- MULTICLOUD METADATA ------------------------------------------------------

DROP VIEW IF EXISTS v_airports;

DROP TABLE IF EXISTS airports;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS airport_regions;  

DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS geos;
DROP TABLE IF EXISTS providers;

CREATE TABLE providers (
  provider      TEXT     NOT NULL PRIMARY KEY,
  sort_order    SMALLINT NOT NULL,
  short_name    TEXT     NOT NULL,
  disp_name     TEXT     NOT NULL,
  image_file    TEXT     NOT NULL,
  libcloud_name TEXT     NOT NULL
);
INSERT INTO providers VALUES ('aws',   1, 'AWS',     'Amazon Web Services',   'aws.png',   'ec2');
INSERT INTO providers VALUES ('azr',   2, 'Azure',   'Microsoft Azure',       'azure.png', 'azure');
INSERT INTO providers VALUES ('gcp',   3, 'GCP',     'Google Cloud Platform', 'gcp.png',   'gcp');
INSERT INTO providers VALUES ('eqn',   4, 'Equinix', 'Equinix Metal',         'eqnx.png',  'equinixmetal');
INSERT INTO providers VALUES ('akm',   5, 'Akamai',  'Akamai Linode',         'akamai.png','linode');

CREATE TABLE geos (
  geo    TEXT     NOT NULL PRIMARY KEY,
  geo_nm TEXT     NOT NULL
);
INSERT INTO geos VALUES ('na', 'North America');
INSERT INTO geos VALUES ('sa', 'South America');
INSERT INTO geos VALUES ('eu', 'Europe');
INSERT INTO geos VALUES ('ap', 'Asia Pacific');
INSERT INTO geos VALUES ('me', 'Middle East');
INSERT INTO geos VALUES ('au', 'Australia');
INSERT INTO geos VALUES ('af', 'Africa');


CREATE TABLE countries (
  country      TEXT     NOT NULL PRIMARY KEY,
  geo          TEXT     NOT NULL REFERENCES geos(geo),
  country_nm   TEXT     NOT NULL
);
INSERT INTO countries VALUES ('us', 'na', 'United States');
INSERT INTO countries VALUES ('ca', 'na', 'Canada');
INSERT INTO countries VALUES ('br', 'sa', 'Brazil');
INSERT INTO countries VALUES ('ir', 'eu', 'Ireland');
INSERT INTO countries VALUES ('gb', 'eu', 'Great Britain');
INSERT INTO countries VALUES ('de', 'eu', 'Germany');
INSERT INTO countries VALUES ('fr', 'eu', 'France');
INSERT INTO countries VALUES ('it', 'eu', 'Italy');
INSERT INTO countries VALUES ('se', 'eu', 'Sweden');
INSERT INTO countries VALUES ('bh', 'me', 'Bahrain');
INSERT INTO countries VALUES ('ae', 'me', 'UAE');
INSERT INTO countries VALUES ('au', 'au', 'Australia');
INSERT INTO countries VALUES ('za', 'af', 'South Africa');
INSERT INTO countries VALUES ('jp', 'ap', 'Japan');
INSERT INTO countries VALUES ('hk', 'ap', 'Hong Kong');
INSERT INTO countries VALUES ('sg', 'ap', 'Singapore');
INSERT INTO countries VALUES ('kr', 'ap', 'South Korea');
INSERT INTO countries VALUES ('id', 'ap', 'Indonesia');
INSERT INTO countries VALUES ('in', 'ap', 'India');
INSERT INTO countries VALUES ('nz', 'au', 'New Zealand');
INSERT INTO countries VALUES ('cn', 'ap', 'China');
INSERT INTO countries VALUES ('es', 'eu', 'Spain');
INSERT INTO countries VALUES ('il', 'me', 'Israel');
INSERT INTO countries VALUES ('be', 'eu', 'Belgium');
INSERT INTO countries VALUES ('nl', 'eu', 'Netherlands');
INSERT INTO countries VALUES ('fl', 'eu', 'Finland');
INSERT INTO countries VALUES ('tw', 'ap', 'Taiwan');
INSERT INTO countries VALUES ('cl', 'sa', 'Chile');
INSERT INTO countries VALUES ('pl', 'eu', 'Poland');
INSERT INTO countries VALUES ('no', 'eu', 'Norway');
INSERT INTO countries VALUES ('qa', 'me', 'Qatar');


CREATE TABLE airports (
  airport       TEXT     NOT NULL NOT NULL PRIMARY KEY,
  airport_area  TEXT     NOT NULL,
  country       TEXT     NOT NULL REFERENCES countries(country),
  lattitude     FLOAT    NOT NULL,
  longitude     FLOAT    NOT NULL
);
INSERT INTO airports VALUES ('iad', 'Northern Virginia',  'us',   38.9519,  -77.4480);
INSERT INTO airports VALUES ('cmh', 'Ohio',               'us',   39.9950,  -82.8891);
INSERT INTO airports VALUES ('pdt', 'Oregon',             'us',   45.6947, -118.8430);
INSERT INTO airports VALUES ('sfo', 'Silicon Valley',     'us',   37.6213, -122.3789);
INSERT INTO airports VALUES ('atl', 'Atlanta',            'us',   33.6404,  -84.4198);
INSERT INTO airports VALUES ('bos', 'Boston',             'us',   42.3669,  -71.0223);
INSERT INTO airports VALUES ('chi', 'Chicago',            'us',   41.9786,  -87.9047);
INSERT INTO airports VALUES ('dfw', 'Dallas',             'us',   32.8481,  -96.8513);
INSERT INTO airports VALUES ('den', 'Denver',             'us',   39.8560, -104.6737);
INSERT INTO airports VALUES ('iah', 'Houston',            'us',   36.9428, -109.7071);
INSERT INTO airports VALUES ('mci', 'Kansas City',        'us',   39.2970,  -94.6903);
INSERT INTO airports VALUES ('lax', 'Los Angeles',        'us',   33.9427, -118.4100);
INSERT INTO airports VALUES ('las', 'Las Vegas',          'us',   36.0860, -115.1539);
INSERT INTO airports VALUES ('mia', 'Miami',              'us',   25.7958,  -80.2870);
INSERT INTO airports VALUES ('msp', 'Minneapolis',        'us',   44.8843,  -93.2140);
INSERT INTO airports VALUES ('jfk', 'New York City',      'us',   40.6417,  -73.7809);
INSERT INTO airports VALUES ('phl', 'Philadelphia',       'us',   39.8741,  -75.2472);
INSERT INTO airports VALUES ('phx', 'Phoenix',            'us',   33.4372, -112.0077);
INSERT INTO airports VALUES ('pdx', 'Portland',           'us',   45.5875, -122.5933);
INSERT INTO airports VALUES ('sea', 'Seattle',            'us',   47.4435, -122.3016);
INSERT INTO airports VALUES ('slc', 'Salt Lake City',     'us',   40.7899, -111.9791);
INSERT INTO airports VALUES ('dsm', 'Iowa',               'us',   41.5341,  -93.6588);
INSERT INTO airports VALUES ('chs', 'Charleston',         'us',   32.8943,  -80.0382);
INSERT INTO airports VALUES ('jac', 'Wyoming',            'us',   43.6034, -110.7363);
INSERT INTO airports VALUES ('ric', 'Central Virginia',   'us',   37.5066,  -77.3208);
INSERT INTO airports VALUES ('ewr', 'Newark, NJ',         'us',   40.6895,  -74.1745);


INSERT INTO airports VALUES ('yul', 'Montreal',           'ca',   45.5019,  -73.5616);
INSERT INTO airports VALUES ('yyz', 'Toronto',            'ca',   43.6777,  -79.6248);
INSERT INTO airports VALUES ('yow', 'Ottowa',             'ca',   45.3223,  -75.6674);
INSERT INTO airports VALUES ('ysj', 'Saint John',         'ca',   45.2733,  -66.0633);
INSERT INTO airports VALUES ('yys', 'Calgary',            'ca',   51.1215, -114.0000);
INSERT INTO airports VALUES ('yvr', 'Vancouver',          'ca',   49.1902, -123.1837);

INSERT INTO airports VALUES ('gru', 'Sao Paulo',          'br',  -23.5337,  -46.6252);
INSERT INTO airports VALUES ('gig', 'Rio de Janeiro',     'br',  -22.8053,  -43.2395);

INSERT INTO airports VALUES ('dub', 'Dublin',             'ir',   53.4264,   -6.2499);
INSERT INTO airports VALUES ('lhr', 'London',             'gb',   51.4603,   -0.4390);
INSERT INTO airports VALUES ('man', 'Manchester',         'gb',   53.3590,   -2.2705);
INSERT INTO airports VALUES ('cwl', 'Cardiff',            'gb',   51.3985,    3.3397);
INSERT INTO airports VALUES ('fra', 'Frankfurt',          'de',   50.0379,    8.5621);
INSERT INTO airports VALUES ('arn', 'Stockholm',          'se',   59.6497,   17.9237);
INSERT INTO airports VALUES ('cdg', 'Paris',              'fr',   49.0097,    2.5477);
INSERT INTO airports VALUES ('mxp', 'Milan',              'it',   45.6286,    8.7236);
INSERT INTO airports VALUES ('mad', 'Madrid',             'es',   40.4840,   -3.5680);
INSERT INTO airports VALUES ('zrh', 'Zurich',             'se',   47.4515,    8.5646);
INSERT INTO airports VALUES ('bru', 'Brussels',           'be',   50.9010,    4.4856);
INSERT INTO airports VALUES ('ams', 'Amsterdam',          'nl',   52.3105,    4.7683);
INSERT INTO airports VALUES ('hel', 'Helsinki',           'fl',   60.3183,   24.9497);
INSERT INTO airports VALUES ('waw', 'Warsaw',             'pl',   52.1672,   20.9679);
INSERT INTO airports VALUES ('osl', 'Oslo',               'no',   60.1976,   11.0004);

INSERT INTO airports VALUES ('cpt', 'Cape Town',          'za',  -33.9725,   18.6019);
INSERT INTO airports VALUES ('jnb', 'Johannesburg',       'za',  -26.1367,   28.2411);
INSERT INTO airports VALUES ('scl', 'Santiago',           'cl',  -33.3898,  -70.7945);

INSERT INTO airports VALUES ('akl', 'Auckland',           'nz',  -36.9993,  174.7879);
INSERT INTO airports VALUES ('syd', 'Sydney',             'au',  -33.9399,  151.1752);
INSERT INTO airports VALUES ('mel', 'Melbourne',          'au',  -37.6637,  144.8448);
INSERT INTO airports VALUES ('cbr', 'Canberra',           'au',  -35.3052,  149.1934);

INSERT INTO airports VALUES ('bah', 'Bahrain',            'bh',   26.2697,   50.6259);
INSERT INTO airports VALUES ('auh', 'UAE',                'ae',   24.4329,   54.6445);
INSERT INTO airports VALUES ('doh', 'Doha',               'qa',   25.2609,   51.6138);
INSERT INTO airports VALUES ('tlv', 'Tel Aviv',           'il',   32.0055,   34.8854);

INSERT INTO airports VALUES ('nrt', 'Tokyo',              'jp',   35.7719,  140.3928);
INSERT INTO airports VALUES ('itm', 'Osaka',              'jp',   34.4338,  135.2263);
INSERT INTO airports VALUES ('icn', 'Seoul',              'kr',   37.4601,  126.4406);

INSERT INTO airports VALUES ('sin', 'Singapore',          'sg',    1.4201,  103.8645);
INSERT INTO airports VALUES ('cgk', 'Jakarta',            'id',   -6.1256,  106.6558);

INSERT INTO airports VALUES ('hyd', 'Hyderabad',          'in',   17.2403,   78.4294);
INSERT INTO airports VALUES ('bom', 'Mumbai',             'in',   19.0901,   72.8687);
INSERT INTO airports VALUES ('del', 'Delhi',              'in',   28.5562,   77.1000);
INSERT INTO airports VALUES ('pnq', 'Pune',               'in',   18.5793,   73.9089);
INSERT INTO airports VALUES ('maa', 'Chennai',            'in',   12.9941,   80.1707);

INSERT INTO airports VALUES ('hkg', 'Hong Kong',          'hk',   22.3080,  113.9184);
INSERT INTO airports VALUES ('tpe', 'Taiwan',             'tw',   25.0797,  121.2342);
INSERT INTO airports VALUES ('pvg', 'Shanghai',           'cn',   31.1443,  121.8083);
INSERT INTO airports VALUES ('pek', 'Beijing',            'cn',   40.0725,  116.5974);
INSERT INTO airports VALUES ('csx', 'Changsha',           'cn',   28.1913,  113.2192);


CREATE TABLE airport_regions  (
  provider      TEXT  NOT NULL REFERENCES providers(provider),
  airport       TEXT  NOT NULL REFERENCES airports(airport),
  region        TEXT  NOT NULL,
  parent        TEXT  NOT NULL,
  zones         TEXT  NOT NULL,
  is_active     TEXT  NOT NULL,
  PRIMARY KEY (provider, airport)
);
INSERT INTO airport_regions VALUES ('eqn', 'iad', 'Washington DC', '', 'dc1,dc2,dc3,dc4,dc5,dc6,dc7,dc10,dc11,dc12,dc13,dc14,dc15,dc21,dc97', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'bos', 'Boston',        '', 'bo1,bo2', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'yow', 'Ottowa',        '', 'ot1', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'yul', 'Montreal',      '', 'mt1', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'ysj', 'Saint John',    '', 'sj1', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'sea', 'Seattle',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'hel', 'Helsinki',      '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'hkg', 'Hong Kong',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'ams', 'Amsterdam',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'jfk', 'New York',      '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'nrt', 'Tokyo',         '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'atl', 'Atlanta',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'icn', 'Seoul',         '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'mad', 'Madrid',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'gru', 'Sao Paulo',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'fra', 'Frankfurt',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'syd', 'Sydney',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'lhr', 'London',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'sin', 'Singapore',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'arn', 'Stockholm',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'cdg', 'Paris',         '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'yyz', 'Toronto',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'mel', 'Melbourne',     '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'itn', 'Osaka',         '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'man', 'Manchester',    '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'mia', 'Miami',         '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'bom', 'Mumbai',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'sfo', 'Silicon Valley','', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'lax', 'Los Angeles',   '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'ohr', 'Chicago',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('eqn', 'dfw', 'Dallas',        '', '', 'Y');


INSERT INTO airport_regions VALUES ('akm', 'bom', 'ap-west',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'maa', 'in-maa',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'cgk', 'in-cgk',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'itm', 'jp-osm',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'syd', 'ap-southest',   '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'sin', 'ap-south',      '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'nrt', 'ap-northeast',  '', '', 'Y');

INSERT INTO airport_regions VALUES ('akm', 'yyz', 'ca-central',    '', '', 'Y');

INSERT INTO airport_regions VALUES ('akm', 'dfw', 'us-central',  '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'sfo', 'us-west',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'atl', 'us-southest',   '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'ewr', 'us-east',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'iad', 'us-iad',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'chi', 'us-ord',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'lax', 'us-lax',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'mia', 'us-mia',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'sea', 'us-sea',        '', '', 'Y');

INSERT INTO airport_regions VALUES ('akm', 'lhr', 'eu-west',       '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'mxp', 'it-mil',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'cdg', 'fr-par',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'ams', 'nl-ams',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'arn', 'se-sto',        '', '', 'Y');
INSERT INTO airport_regions VALUES ('akm', 'fra', 'eu-central',    '', '', 'Y');


INSERT INTO airport_regions VALUES ('akm', 'gru', 'br-gru',        '', '', 'Y');

INSERT INTO airport_regions VALUES ('aws', 'iad', 'us-east-1', '',                'a,b,c,d,e,f', 'Y');
INSERT INTO airport_regions VALUES ('aws', 'dfw', 'us-east-1', 'us-east-1-dfw-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'atl', 'us-east-1', 'us-east-1-atl-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'bos', 'us-east-1', 'us-east-1-bos-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'chi', 'us-east-1', 'us-east-1-chi-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'iah', 'us-east-1', 'us-east-1-iah-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'mci', 'us-east-1', 'us-east-1-mci-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'mia', 'us-east-1', 'us-east-1-mia-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'msp', 'us-east-1', 'us-east-1-msp-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'jfk', 'us-east-1', 'us-east-1-nyc-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'phl', 'us-east-1', 'us-east-1-phl-1', 'a',           'Y');

INSERT INTO airport_regions VALUES ('aws', 'cmh', 'us-east-2', '',                'a,b,c',       'Y');

INSERT INTO airport_regions VALUES ('aws', 'sfo', 'us-west-1', '',                'a,b,c',       'Y');

INSERT INTO airport_regions VALUES ('aws', 'pdt', 'us-west-2', '',                'a,b,c,d',     'Y');
INSERT INTO airport_regions VALUES ('aws', 'las', 'us-west-2', 'us-west-2-las-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'lax', 'us-west-2', 'us-west-2-lax-1', 'a,b',         'Y');
INSERT INTO airport_regions VALUES ('aws', 'den', 'us-west-2', 'us-west-2-den-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'phx', 'us-west-2', 'us-west-2-phx-1', 'a',           'Y');
INSERT INTO airport_regions VALUES ('aws', 'pdx', 'us-west-2', 'us-west-2-pdx-1', 'a',           'Y');


INSERT INTO airport_regions VALUES ('aws', 'mtl', 'ca-central-1',   '',           'a,b',         'Y');

INSERT INTO airport_regions VALUES ('aws', 'sin', 'ap-southeast-1', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'icn', 'ap-northeast-2', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'hkg', 'ap-east-1',      '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'itm', 'ap-northeast-3', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'nrt', 'ap-northeast-1', '',           'a,b,c,d',     'Y');
INSERT INTO airport_regions VALUES ('aws', 'bom', 'ap-south-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'yyc', 'ca-west-1',      '',           'a,b',         'N');
INSERT INTO airport_regions VALUES ('aws', 'akl', 'ap-southeast-5', '',           'a,b,c',       'N');
INSERT INTO airport_regions VALUES ('aws', 'cgk', 'ap-southeast-3', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'mel', 'ap-southeast-4', '',           'a,b,c',       'N');
INSERT INTO airport_regions VALUES ('aws', 'syd', 'ap-southeast-2', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'hyd', 'ap-south-2',     '',           'a,b,c',       'N');
INSERT INTO airport_regions VALUES ('aws', 'gru', 'sa-east-1',      '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'fra', 'eu-central-1',   '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'dub', 'eu-west-1',      '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'lhr', 'eu-west-2',      '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'mxp', 'eu-south-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'cdg', 'eu-west-3',      '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'mad', 'eu-east-1',      '',           'a,b,c',       'N');
INSERT INTO airport_regions VALUES ('aws', 'arn', 'eu-north-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'zrh', 'eu-central-2',   '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'pek', 'cn-north-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'csx', 'cn-northwest-1', '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'cpt', 'af-south-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'bah', 'me-south-1',     '',           'a,b,c',       'Y');
INSERT INTO airport_regions VALUES ('aws', 'tlv', 'me-west-1',      '',           'a,b,c',       'N');
INSERT INTO airport_regions VALUES ('aws', 'auh', 'me-south-2',     '',           'a,b,c',       'N');

INSERT INTO airport_regions VALUES ('gcp', 'pdt', 'us-west1',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'lax', 'us-west2',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'slc', 'us-west3',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'las', 'us-west4',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'dsm', 'us-central1',             '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'chs', 'us-east1',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'iad', 'us-east4',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'cmh', 'us-east5',                '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'dfw', 'us-south1',               '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'mtl', 'northamerica-northeast1', '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'yyz', 'northamerica-northeast2', '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'gru', 'southamerica-east1',      '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'scl', 'southamerica-west1',      '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'lhr', 'europe-west2',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'bru', 'europe-west1',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'ams', 'europe-west4',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'zrh', 'europe-west6',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'fra', 'europe-west3',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'hel', 'europe-north1',           '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'waw', 'europe-central2',         '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'mil', 'europe-west8',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'mad', 'europe-southwest1',       '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'cdg', 'europe-west9',            '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'bom', 'asia-south1',             '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'del', 'asia-south2',             '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'sin', 'asia-southeast1',         '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'cgk', 'asia-southeast2',         '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'hkg', 'asia-east2',              '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'tpe', 'asia-east1',              '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'nrt', 'asia-northeast1',         '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'itm', 'asia-northeast2',         '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'syd', 'australia-southeast1',    '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'mel', 'australia-southeast2',    '', 'a,b,c', 'Y');
INSERT INTO airport_regions VALUES ('gcp', 'icn', 'asia-northeast3',         '', 'a,b,c', 'Y');

INSERT INTO airport_regions VALUES ('azr', 'sea', 'westus2',            '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'lax', 'westus',             '', 'a,b,c',  'N');
INSERT INTO airport_regions VALUES ('azr', 'phx', 'westus3',            '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'jac', 'westcentralus',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'dsm', 'centralus',          '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'dfw', 'southcentralus',     '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'chi', 'northcentralus',     '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'iad', 'eastus',             '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'ric', 'eastus2',            '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'yyz', 'canadacentral',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'mtl', 'canadaeast',         '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'gru', 'brazilsouth',        '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'jnb', 'southafricanorth',   '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'dub', 'northeurope',        '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'cwl', 'ukwest',             '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'lhr', 'uksouth',            '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'cdg', 'francecentral',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'arn', 'swedencentral',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'osl', 'norwayeast',         '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'ams', 'westeurope',         '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'fra', 'germanywestcentral', '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'zrh', 'switzerlandnorth',   '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'doh', 'qatarcentral',       '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'auh', 'UAEnorth',           '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'png', 'centralindia',       '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'maa', 'southindia',         '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'sin', 'southeastasia',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'hkg', 'eastasia',           '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'pvg', 'chinaeast',          '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'pek', 'chinanorth',         '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'icn', 'koreacentral',       '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'itm', 'japanwest',          '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'nrt', 'japaneast',          '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'syd', 'australiaeast',      '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'mel', 'australiasoutheast', '', 'a,b,c',  'Y');
INSERT INTO airport_regions VALUES ('azr', 'cbr', 'australiacentral',   '', 'a,b,c',  'Y');


CREATE VIEW v_airports AS
SELECT g.geo, c.country, a.airport, a.airport_area, a.lattitude, a.longitude,
       ar.provider, ar.region, ar.parent, ar.zones
  FROM geos g, countries c, airport_regions ar, airports a
 WHERE g.geo = c.geo 
   AND c.country = a.country 
   AND a.airport  = ar.airport
ORDER BY 1, 2, 3, 4, 5;

