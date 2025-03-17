
DROP TABLE IF EXISTS hub;
CREATE TABLE hub(v TEXT NOT NULL PRIMARY KEY, c TEXT NOT NULL, d TEXT NOT NULL);
INSERT INTO hub VALUES ('24.10.12', 'Constellation',  '20250314');

DROP VIEW  IF EXISTS v_versions;
DROP VIEW  IF EXISTS v_products;

DROP TABLE IF EXISTS products;

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
  aliases        TEXT     NOT NULL,
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
   spock.save_resolutions=on | spock.conflict_log_level=DEBUG');
INSERT INTO extensions VALUES ('spock40', 'spock', 1, 'spock',
  'wal_level=logical | max_worker_processes=12 | max_replication_slots=16 |
   max_wal_senders=16 | hot_standby_feedback=on | wal_sender_timeout=5s |
   track_commit_timestamp=on | spock.conflict_resolution=last_update_wins | 
   spock.save_resolutions=on | spock.conflict_log_level=DEBUG');
INSERT INTO extensions VALUES ('spock41', 'spock', 1, 'spock',
  'wal_level=logical | max_worker_processes=12 | max_replication_slots=16 |
   max_wal_senders=16 | hot_standby_feedback=on | wal_sender_timeout=5s |
   track_commit_timestamp=on | spock.conflict_resolution=last_update_wins | 
   spock.save_resolutions=on | spock.conflict_log_level=DEBUG');
INSERT INTO extensions VALUES ('lolor',     'lolor',     0, '',          '');
INSERT INTO extensions VALUES ('postgis',   'postgis',   1, 'postgis-3', '');
INSERT INTO extensions VALUES ('setuser',   'set_user',  1, 'set_user',  '');
INSERT INTO extensions VALUES ('orafce',    'orafce',    1, 'orafce',    '');
INSERT INTO extensions VALUES ('snowflake', 'snowflake', 1, 'snowflake', '');

INSERT INTO extensions VALUES ('vector',    'vector',       0, '',               '');
INSERT INTO extensions VALUES ('wal2json',  'wal2json',     1, 'wal2json',       '');
INSERT INTO extensions VALUES ('timescaledb','timescaledb', 1, 'timescaledb', 'timescaledb.telemetry_level=off'); 
INSERT INTO extensions VALUES ('permissions','pg_permissions', 0, '',               '');
INSERT INTO extensions VALUES ('citus',      'citus',       1, 'citus', 'citus.enable_statistics_collection=off');

INSERT INTO extensions VALUES ('audit',     'pgaudit',      1, 'pgaudit',        '');
INSERT INTO extensions VALUES ('partman',   'pg_partman',   1, 'pg_partman_bgw', '');
INSERT INTO extensions VALUES ('hintplan',  'pg_hint_plan', 1, 'pg_hint_plan',   '');
INSERT INTO extensions VALUES ('cron',      'pg_cron',      1, 'pg_cron',        '');
INSERT INTO extensions VALUES ('hypopg',    'hypopg',       1, 'hypopg',         '');
INSERT INTO extensions VALUES ('plv8',      'plv8',         0, '',               '');
INSERT INTO extensions VALUES ('pldebugger','pldbgapi',     1, 'plugin_debugger','');
INSERT INTO extensions VALUES ('plprofiler','plprofiler',   1, 'plprofiler',     '');


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

-- ## HUB ################################
INSERT INTO projects VALUES ('hub', 'app', 0, 0, 'hub', 0, 'https://github.com/pgedge/cli','',0,'','','','');
INSERT INTO releases VALUES ('hub', 1, 'hub',  '', '', 'hidden', '', 1, '', '', '');

INSERT INTO versions VALUES ('hub', (select v from hub), '',  1, (select d from hub), '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.11',  '',  0, '20250224', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.10',  '',  0, '20250123', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.9',   '',  0, '20241206', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.7',   '',  0, '20241125', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.6',   '',  0, '20241120', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.5',   '',  0, '20241107', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.4',   '',  0, '20241105', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.3',   '',  0, '20241104', '', '', '');
INSERT INTO versions VALUES ('hub', '24.10.2',   '',  0, '20241002', '', '', '');
INSERT INTO versions VALUES ('hub', '24.9.6',    '',  0, '20240919', '', '', '');
INSERT INTO versions VALUES ('hub', '24.7.7',    '',  0, '20240820', '', '', '');
INSERT INTO versions VALUES ('hub', '24.7.6',    '',  0, '20240731', '', '', '');
INSERT INTO versions VALUES ('hub', '24.7.4',    '',  0, '20240710', '', '', '');

-- ## PG #################################
INSERT INTO projects VALUES ('pg', 'pge', 1, 5432, '', 1, 'https://github.com/postgres/postgres/tags',
 'postgres', 0, 'postgresql.png', 'Best RDBMS', 'https://postgresql.org', '');

INSERT INTO releases VALUES ('pg15', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/15/release-15.html>2022</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg15', '15.12-1',  'amd, arm', 1, '20250224','', '', '');
INSERT INTO versions VALUES ('pg15', '15.10-1',  'amd, arm', 0, '20241121','', '', '');

INSERT INTO releases VALUES ('pg16', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/16/release-16.html>2023!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg16', '16.8-1',  'amd, arm', 1, '20250224','', '', '');
INSERT INTO versions VALUES ('pg16', '16.6-1',  'amd, arm', 0, '20241121','', '', '');

INSERT INTO releases VALUES ('pg17', 2, 'pg', '', '', 'prod', 
  '<font size=-1>New in <a href=https://www.postgresql.org/docs/17/release-17.html>2024!</a></font>', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('pg17', '17.4-1',    'amd, arm', 1, '20250224','', '', '');
INSERT INTO versions VALUES ('pg17', '17.2-1',    'amd, arm', 0, '20241121','', '', '');

-- ## ORAFCE #############################
INSERT INTO projects VALUES ('orafce', 'ext', 4, 0, '', 0, 'https://github.com/orafce/orafce/releases',
  'orafce', 1, 'larry.png', 'Ora Built-in Packages', 'https://github.com/orafce/orafce#orafce---oracles-compatibility-functions-and-packages', 'orafice, oraface');
INSERT INTO releases VALUES ('orafce-pg15', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('orafce-pg16', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('orafce-pg17', 2, 'orafce', 'OraFCE', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('orafce-pg15', '4.13.4-1',   'amd, arm', 1, '20241104', 'pg15', '', '');
INSERT INTO versions VALUES ('orafce-pg16', '4.13.4-1',   'amd, arm', 1, '20241104', 'pg16', '', '');
INSERT INTO versions VALUES ('orafce-pg17', '4.13.4-1',   'amd, arm', 1, '20241104', 'pg17', '', '');

-- ## PLV8 ###############################
INSERT INTO projects VALUES ('plv8', 'dev', 4, 0, '', 0, 'https://github.com/plv8/plv8/tags',
  'plv8',   1, 'v8.png', 'Javascript Stored Procedures', 'https://github.com/plv8/plv8', 'pl_v8');
INSERT INTO releases VALUES ('plv8-pg15', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plv8-pg16', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plv8-pg17', 4, 'plv8', 'PL/V8', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('plv8-pg15', '3.2.3-1', 'amd, arm', 1, '20241104', 'pg15', '', '');
INSERT INTO versions VALUES ('plv8-pg16', '3.2.3-1', 'amd, arm', 1, '20241104', 'pg16', '', '');
INSERT INTO versions VALUES ('plv8-pg17', '3.2.3-1', 'amd, arm', 1, '20241104', 'pg17', '', '');

-- ## PLDEBUGGER #########################
INSERT INTO projects VALUES ('pldebugger', 'dev', 4, 0, '', 0, 'https://github.com/EnterpriseDB/pldebugger/tags',
  'pldebugger', 1, 'debugger.png', 'Stored Procedure Debugger', 'https://github.com/EnterpriseDB/pldebugger', 'pl_debugger, dbgapi');
INSERT INTO releases VALUES ('pldebugger-pg15', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pldebugger-pg16', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('pldebugger-pg17', 2, 'pldebugger', 'PL/Debugger', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('pldebugger-pg17', '1.8-1',  'amd, arm',  1, '20240905', 'pg17', '', '');
INSERT INTO versions VALUES ('pldebugger-pg16', '1.8-1',  'amd, arm',  1, '20240905', 'pg16', '', '');
INSERT INTO versions VALUES ('pldebugger-pg15', '1.8-1',  'amd, arm',  1, '20240905', 'pg15', '', '');

-- ## PLPROFILER #########################
INSERT INTO projects VALUES ('plprofiler', 'dev', 4, 0, '', 7, 'https://github.com/bigsql/plprofiler/tags',
  'plprofiler', 1, 'plprofiler.png', 'Stored Procedure Profiler', 'https://github.com/bigsql/plprofiler#plprofiler', 'pl_profiler');
INSERT INTO releases VALUES ('plprofiler-pg15', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg16', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('plprofiler-pg17', 0, 'plprofiler',    'PL/Profiler',  '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('plprofiler-pg17', '4.2.5-1', 'amd, arm', 1, '20240820', 'pg17', '', '');
INSERT INTO versions VALUES ('plprofiler-pg16', '4.2.5-1', 'amd, arm', 1, '20240820', 'pg16', '', '');
INSERT INTO versions VALUES ('plprofiler-pg15', '4.2.5-1', 'amd, arm', 1, '20240820', 'pg15', '', '');

-- ## PROMPGEXP ##########################
INSERT INTO projects VALUES ('prompgexp', 'pge', 11, 9187, 'golang', 0, 'https://github.com/prometheus-community/postgres_exporter/releases',
  'prompgexp', 0, 'prometheus.png', 'Prometheus PG Exporter', 'https://github.com/prometheus-community/postgres_exporter', 'postgres_exporter, prometheus, exporter');
INSERT INTO releases VALUES ('prompgexp', 9, 'prompgexp', 'Prometheus Postgres Exporter', '', 'test', '', 1, 'Apache', '', '');
INSERT INTO versions VALUES ('prompgexp', '0.15.0', 'amd, arm', 1, '20240521', '', '', 'https://github.com/prometheus-community/postgres_exporter');

-- ## AUDIT ##############################
INSERT INTO projects VALUES ('audit', 'ext', 4, 0, '', 0, 'https://github.com/pgaudit/pgaudit/releases',
  'audit', 1, 'audit.png', 'Audit Logging', 'https://github.com/pgaudit/pgaudit', 'pg_audit, pgaudit');
INSERT INTO releases VALUES ('audit-pg17', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('audit-pg16', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('audit-pg15', 10, 'audit', 'pgAudit', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('audit-pg17', '17.0-1',  'amd, arm', 1, '20240912', 'pg17', '', 'https://github.com/pgaudit/pgaudit/releases/tag/17.0');
INSERT INTO versions VALUES ('audit-pg16', '16.0-1',  'amd, arm', 1, '20230914', 'pg16', '', 'https://github.com/pgaudit/pgaudit/releases/tag/16.0');
INSERT INTO versions VALUES ('audit-pg15', '1.7.0-1', 'amd, arm', 1, '20230914', 'pg15', '', 'https://github.com/pgaudit/pgaudit/releases/tag/1.7.0');

-- ## WAL2JSON ###########################
INSERT INTO projects VALUES ('wal2json', 'ext', 4, 0, '', 0, 'https://github.com/eulerto/wal2json/tags',
  'wal2json', 1, 'wal2json.png', 'WAL to JSON for CDC', 'https://github.com/eulerto/wal2json', 'wal2_json, wal_2_json');
INSERT INTO releases VALUES ('wal2json-pg15', 10, 'wal2json', 'wal2json', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('wal2json-pg16', 10, 'wal2json', 'wal2json', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('wal2json-pg15', '2.6.0-1', 'amd, arm', 1, '20240509', 'pg15', '', 'https://github.com/eulerto/wal2json/tags');
INSERT INTO versions VALUES ('wal2json-pg16', '2.6.0-1', 'amd, arm', 1, '20240509', 'pg16', '', 'https://github.com/eulerto/wal2json/tags');

-- ## HINTPLAN ###########################
INSERT INTO projects VALUES ('hintplan', 'ext', 4, 0, '', 0, 'https://github.com/ossc-db/pg_hint_plan/tags',
  'hintplan', 1, 'hintplan.png', 'Execution Plan Hints', 'https://github.com/ossc-db/pg_hint_plan', 'pg_hintplan, pg_hint_plan');
INSERT INTO releases VALUES ('hintplan-pg17', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hintplan-pg16', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hintplan-pg15', 10, 'hintplan', 'pgHintPlan', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('hintplan-pg17', '1.7.0-1', 'amd, arm', 1, '20240910', 'pg17', '', '');
INSERT INTO versions VALUES ('hintplan-pg16', '1.6.1-1', 'amd, arm', 1, '20240910', 'pg16', '', '');
INSERT INTO versions VALUES ('hintplan-pg15', '1.5.2-1', 'amd, arm', 1, '20240910', 'pg15', '', '');

-- ## TIMESCALEDB #######################
INSERT INTO projects VALUES ('timescaledb', 'ext', 4, 0, '',0, 'https://github.com/timescale/timescaledb/releases',
  'timescaledb', 1, 'timescaledb.png', 'Timeseries Extension', 'https://github.com/timescaledb/timescaledb', 'timescale_db, time_scale_db');
INSERT INTO releases VALUES ('timescaledb-pg15', 10, 'timescaledb', 'TimescaleDB', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('timescaledb-pg16', 10, 'timescaledb', 'TimescaleDB', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('timescaledb-pg17', 10, 'timescaledb', 'TimescaleDB', '', 'test', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('timescaledb-pg15', '2.17.0-1', 'amd, arm', 1, '20241104', 'pg15', '', '');
INSERT INTO versions VALUES ('timescaledb-pg16', '2.17.0-1', 'amd, arm', 1, '20241104', 'pg16', '', '');
INSERT INTO versions VALUES ('timescaledb-pg17', '2.17.0-1', 'amd, arm', 1, '20241104', 'pg17', '', '');

-- ## CURL ##############################
INSERT INTO projects VALUES ('curl', 'ext', 4, 0, '',0, 'https://github.com/pg_curl/pg_curl/releases',
  'curl', 1, 'curl.png', 'Invoke JSON Services', 'https://github.com/pg_curl/pg_curl', 'pg_curl');
INSERT INTO releases VALUES ('curl-pg15', 10, 'curl', 'pgCron', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('curl-pg16', 10, 'curl', 'pgCron', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('curl-pg15', '2.2.2-1',  'amd, arm', 0, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('curl-pg16', '2.2.2-1',  'amd, arm', 0, '20240130', 'pg16', '', '');

-- ## CITUS #############################
INSERT INTO projects VALUES ('citus', 'pge', 4, 0, '',0, 'https://github.com/citusdata/citus/releases',
  'citus', 1, 'citus.png', 'Sharded Postgres', 'https://github.com/citusdata/citus', 'citusdata, citus_data');
INSERT INTO releases VALUES ('citus-pg15', 10, 'citus', 'Citus', '', 'test', '', 1, 'AGPLv3', '', '');
INSERT INTO releases VALUES ('citus-pg16', 10, 'citus', 'Citus', '', 'test', '', 1, 'AGPLv3', '', '');

INSERT INTO versions VALUES ('citus-pg15', '12.1.5-1', 'amd, arm', 1, '20240729', 'pg15', '', '');
INSERT INTO versions VALUES ('citus-pg16', '12.1.5-1', 'amd, arm', 1, '20240729', 'pg16', '', '');

-- ## CRON ##############################
INSERT INTO projects VALUES ('cron', 'ext', 4, 0, '',0, 'https://github.com/citusdata/pg_cron/releases',
  'cron', 1, 'cron.png', 'Background Job Scheduler', 'https://github.com/citusdata/pg_cron', 'pg_cron, pgcron');
INSERT INTO releases VALUES ('cron-pg17', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('cron-pg16', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('cron-pg15', 10, 'cron', 'pgCron', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('cron-pg17', '1.6.4-1', 'amd, arm', 1, '20240910', 'pg17', '', '');
INSERT INTO versions VALUES ('cron-pg16', '1.6.4-1', 'amd, arm', 1, '20240815', 'pg16', '', '');
INSERT INTO versions VALUES ('cron-pg15', '1.6.4-1', 'amd, arm', 1, '20240815', 'pg15', '', '');


-- ## VECTOR ############################
INSERT INTO projects VALUES ('vector', 'pge', 4, 0, '', 1, 'https://github.com/pgedge/vector/tags',
  'vector', 1, 'vector.png', 'Vector & Embeddings', 'https://github.com/pgedge/vector/#vector', 'pg_vector, pgvector');
INSERT INTO releases VALUES ('vector-pg15', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('vector-pg16', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('vector-pg17', 4, 'vector', 'pgVector', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('vector-pg15', '0.8.0-1', 'amd, arm', 1, '20241101', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.8.0-1', 'amd, arm', 1, '20241101', 'pg16', '', '');
INSERT INTO versions VALUES ('vector-pg17', '0.8.0-1', 'amd, arm', 1, '20241101', 'pg17', '', '');

INSERT INTO versions VALUES ('vector-pg15', '0.7.4-1', 'amd, arm', 0, '20240820', 'pg15', '', '');
INSERT INTO versions VALUES ('vector-pg16', '0.7.4-1', 'amd, arm', 0, '20240820', 'pg16', '', '');


-- ## SNOWFLAKE #########################
INSERT INTO projects VALUES ('snowflake', 'pge', 4, 0, '', 1, 'https://github.com/pgedge/snowflake/tags',
  'snowflake', 1, 'snowflake.png', 'Snowflake Sequences', 'https://github.com/pgedge/snowflake/', 'pg_snowflake, pgsnowflake');
INSERT INTO releases VALUES ('snowflake-pg15', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg16', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('snowflake-pg17', 4, 'snowflake', 'Snowflake', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('snowflake-pg15', '2.2-1', 'amd, arm', 1, '20240626', 'pg15', '', '');
INSERT INTO versions VALUES ('snowflake-pg16', '2.2-1', 'amd, arm', 1, '20240626', 'pg16', '', '');
INSERT INTO versions VALUES ('snowflake-pg17', '2.2-1', 'amd, arm', 1, '20240626', 'pg17', '', '');


-- ## SPOCK (parent project) ############
INSERT INTO projects VALUES ('spock', 'pge', 4, 0, '', 1, 'https://github.com/pgedge/spock/tags',
  'spock', 1, 'spock.png', 'Logical Rep w/ Conflict Resolution', 'https://github.com/pgedge/spock/', 'pg_spock, pgsspock, vulcan');

-- ## SPOCK33 ###########################
INSERT INTO releases VALUES ('spock33-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock33-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('spock33-pg15', '3.3.6-1', 'amd, arm', 1, '20240820', 'pg15', '', '');
INSERT INTO versions VALUES ('spock33-pg16', '3.3.6-1', 'amd, arm', 1, '20240820', 'pg16', '', '');

INSERT INTO versions VALUES ('spock33-pg15', '3.3.5-1', 'amd, arm', 0, '20240607', 'pg15', '', '');
INSERT INTO versions VALUES ('spock33-pg16', '3.3.5-1', 'amd, arm', 0, '20240607', 'pg16', '', '');

-- ## SPOCK40 ###########################
INSERT INTO releases VALUES ('spock40-pg15', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock40-pg16', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock40-pg17', 4, 'spock', 'Spock', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('spock40-pg15', '4.0.10-1', 'amd, arm', 1, '20250224', 'pg15', '', '');
INSERT INTO versions VALUES ('spock40-pg16', '4.0.10-1', 'amd, arm', 1, '20250224', 'pg16', '', '');
INSERT INTO versions VALUES ('spock40-pg17', '4.0.10-1', 'amd, arm', 1, '20250224', 'pg17', '', '');

INSERT INTO versions VALUES ('spock40-pg15', '4.0.9-1', 'amd, arm', 0, '20241226', 'pg15', '', '');
INSERT INTO versions VALUES ('spock40-pg16', '4.0.9-1', 'amd, arm', 0, '20241226', 'pg16', '', '');
INSERT INTO versions VALUES ('spock40-pg17', '4.0.9-1', 'amd, arm', 0, '20241226', 'pg17', '', '');

INSERT INTO versions VALUES ('spock40-pg15', '4.0.8-1', 'amd, arm', 0, '20241218', 'pg15', '', '');
INSERT INTO versions VALUES ('spock40-pg16', '4.0.8-1', 'amd, arm', 0, '20241218', 'pg16', '', '');
INSERT INTO versions VALUES ('spock40-pg17', '4.0.8-1', 'amd, arm', 0, '20241218', 'pg17', '', '');


-- ## SPOCK41 ###########################
INSERT INTO releases VALUES ('spock41-pg16', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('spock41-pg17', 4, 'spock', 'Spock', '', 'test', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('spock41-pg16', '4.1devel-2',   'amd, arm', 1, '20241107', 'pg16', '', '');
INSERT INTO versions VALUES ('spock41-pg17', '4.1devel-2',   'amd, arm', 1, '20241107', 'pg17', '', '');

-- ## LOLOR #############################
INSERT INTO projects VALUES ('lolor', 'pge', 4, 0, '', 1, 'https://github.com/pgedge/lolor/tags',
  'spock', 1, 'spock.png', 'Logical Replication of Large Objects', 'https://github.com/pgedge/lolor/#spock', 'lola, lolah, kinks');
INSERT INTO releases VALUES ('lolor-pg15', 4, 'lolor', 'LgObjLOgicalRep', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('lolor-pg16', 4, 'lolor', 'LgObjLOgicalRep', '', 'prod', '', 1, 'pgEdge Community', '', '');
INSERT INTO releases VALUES ('lolor-pg17', 4, 'lolor', 'LgObjLOgicalRep', '', 'prod', '', 1, 'pgEdge Community', '', '');

INSERT INTO versions VALUES ('lolor-pg15', '1.2-1', 'amd, arm', 1, '20240521', 'pg15', '', '');
INSERT INTO versions VALUES ('lolor-pg16', '1.2-1', 'amd, arm', 1, '20240521', 'pg16', '', '');
INSERT INTO versions VALUES ('lolor-pg17', '1.2-1', 'amd, arm', 1, '20240521', 'pg17', '', '');

-- ## PERMISSIONS #######################
INSERT INTO projects VALUES ('permissions', 'ext', 4, 1, '', 3, 'https://github.com/cybertec-postgresql/permissions',
  'permissions', 1, 'permissions.png', 'Improved permissions views', 'https://github.com/cybertec-postgresql/permissions', 'set_user');
INSERT INTO releases VALUES ('permissions-pg15', 3, 'permissions', 'Permissions', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('permissions-pg16', 3, 'permissions', 'Permissions', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('permissions-pg15', '1.3-1', 'amd, arm', 1, '20240729', 'pg15', '', '');
INSERT INTO versions VALUES ('permissions-pg16', '1.3-1', 'amd, arm', 1, '20240729', 'pg16', '', '');

-- ## SETUSER ###########################
INSERT INTO projects VALUES ('setuser', 'ext', 4, 1, '', 3, 'https://github.com/pgaudit/set_user',
  'setuser', 1, 'setuser.png', 'Superuser privilege logging', 'https://github.com/pgaudit/set_user', 'set_user');
INSERT INTO releases VALUES ('setuser-pg17', 3, 'setuser', 'SetUser', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('setuser-pg16', 3, 'setuser', 'SetUser', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('setuser-pg15', 3, 'setuser', 'SetUser', '', 'prod', '', 1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('setuser-pg17', '4.1.0-1', 'amd, arm', 1, '20240912', 'pg17', '', '');
INSERT INTO versions VALUES ('setuser-pg16', '4.1.0-1', 'amd, arm', 1, '20240912', 'pg16', '', '');
INSERT INTO versions VALUES ('setuser-pg15', '4.1.0-1', 'amd, arm', 1, '20240912', 'pg15', '', '');

-- ## POSTGIS ###########################
INSERT INTO projects VALUES ('postgis', 'ext', 4, 1, '', 3, 'http://postgis.net/source',
  'postgis', 1, 'postgis.png', 'Spatial Extensions', 'http://postgis.net', 'spatial, geospatial, geo_spatial');
INSERT INTO releases VALUES ('postgis-pg15', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO releases VALUES ('postgis-pg16', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');
INSERT INTO releases VALUES ('postgis-pg17', 3, 'postgis', 'PostGIS', '', 'prod', '', 1, 'GPLv2', '', '');

INSERT INTO versions VALUES ('postgis-pg15', '3.5.0-2', 'amd, arm', 1, '20241021', 'pg15', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.5.0/NEWS');
INSERT INTO versions VALUES ('postgis-pg16', '3.5.0-2', 'amd, arm', 1, '20241021', 'pg16', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.5.0/NEWS');
INSERT INTO versions VALUES ('postgis-pg17', '3.5.0-2', 'amd, arm', 1, '20241021', 'pg17', '', 'https://git.osgeo.org/gitea/postgis/postgis/raw/tag/3.5.0/NEWS');

-- ## PARTMAN ###########################
INSERT INTO projects VALUES ('partman', 'ext', 4, 0, '', 4, 'https://github.com/pgpartman/pg_partman/tags',
  'partman', 1, 'partman.png', 'Partition Management', 'https://github.com/pgpartman/pg_partman#pg-partition-manager', 'pg_partman, partition_manager');
INSERT INTO releases VALUES ('partman-pg15', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('partman-pg16', 6, 'partman', 'pgPartman',   '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('partman-pg15', '5.0.1-1',  'amd, arm', 1, '20240130', 'pg15', '', '');
INSERT INTO versions VALUES ('partman-pg16', '5.0.1-1',  'amd, arm', 1, '20240130', 'pg16', '', '');

-- ## HYPOPG ############################
INSERT INTO projects VALUES ('hypopg', 'ext', 4, 0, '', 8, 'https://github.com/HypoPG/hypopg/releases',
  'hypopg', 1, 'whatif.png', 'Hypothetical Indexes', 'https://hypopg.readthedocs.io/en/latest/', 'pg_hypo, pghypo');
INSERT INTO releases VALUES ('hypopg-pg15', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');
INSERT INTO releases VALUES ('hypopg-pg16', 99, 'hypopg', 'HypoPG', '', 'prod','',  1, 'POSTGRES', '', '');

INSERT INTO versions VALUES ('hypopg-pg15', '1.4.1-1',  'amd, arm', 1, '20240509', 'pg15', '', '');
INSERT INTO versions VALUES ('hypopg-pg16', '1.4.1-1',  'amd, arm', 1, '20230509', 'pg16', '', '');

-- ## CTLIBS ############################
INSERT INTO projects VALUES ('ctlibs', 'pge', 0, 0, '', 3, 'https://github.com/pgedge/cli',
  'ctlibs',  0, 'ctlibs.png', 'ctlibs', 'https://github.com/pgedge/cli', '');
INSERT INTO releases VALUES ('ctlibs', 2, 'ctlibs',  'pgEdge Libs', '', 'prod', '', 1, '', '', '');
INSERT INTO versions VALUES ('ctlibs', '1.6', '', 1, '20240925', '', '', '');

-- ## PGCAT #############################
INSERT INTO projects VALUES ('pgcat', 'pge', 11, 5433, '', 3, 'https://github.com/pgedge/pgcat/tags',
  'cat',  0, 'pgcat.png', 'Connection Pooler', 'https://github.com/pgedge/pgcat', 'pg_cat, cat');
INSERT INTO releases VALUES ('pgcat', 2, 'pgcat',  'pgCat', '', 'test', '', 1, 'MIT', '', '');
INSERT INTO versions VALUES ('pgcat', '1.2.0', 'amd, arm', 1, '20240905', '', 'EL', '');

-- ## BOUNCER ###########################
INSERT INTO projects VALUES ('bouncer', 'pge', 11, 5433, '', 3, 'http://pgbouncer.org',
  'bouncer',  0, 'bouncer.png', 'Lightweight Connnection Pooler', 'http://pgbouncer.org', 'pg_bouncer, pgbouncer');
INSERT INTO releases VALUES ('bouncer', 2, 'bouncer',  'pgBouncer', '', 'test', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('bouncer', '1.23.1-1', 'amd, arm', 1, '20240820', '', 'EL', '');

-- ## BACKREST ##########################
INSERT INTO projects VALUES ('backrest', 'pge', 11, 0, '', 3, 'http://pgbackrest.org',
  'backrest',  0, 'backrest.png', 'Backup & Restore', 'http://pgbackrest.org', 'pg_backrest, pgbackrest');
INSERT INTO releases VALUES ('backrest', 2, 'backrest',  'pgBackRest', '', 'test', '', 1, 'MIT', 'EL', '');

INSERT INTO versions VALUES ('backrest', '2.53.1-1', 'amd, arm', 1, '20240912', '', '', '');
INSERT INTO versions VALUES ('backrest', '2.53-1',   'amd, arm', 0, '20240729', '', '', '');

-- ## PATRONI ###########################
INSERT INTO projects VALUES ('patroni', 'app', 11, 0, '', 4, 'https://github.com/pgedge/pgedge-patroni/release',
  'patroni', 0, 'patroni.png', 'HA', 'https://github.com/pgedge/pgedge-patroni', 'pg_patroni, pgedge_patroni');
INSERT INTO releases VALUES ('patroni', 1, 'patroni', 'pgEdge Patroni', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('patroni', '3.2.2.2-1', '', 1, '20241107', '', 'EL', '');

-- ## ETCD ##############################
INSERT INTO projects VALUES ('etcd', 'app', 11, 2379, '', 4, 'https://github.com/etcd-io/etcd/tags',
  'etcd', 0, 'etcd.png', 'HA', 'https://github.com/etcd-io/etcd', '');
INSERT INTO releases VALUES ('etcd', 1, 'etcd', 'Etcd', '', 'prod', '', 1, 'POSTGRES', '', '');
INSERT INTO versions VALUES ('etcd', '3.5.12-2', 'amd, arm', 1, '20240328', '', 'EL', '');

-- ## KIRK ###############################
INSERT INTO projects VALUES ('kirk', 'dev', 11, 8883, '', 0, 'https://github.com/pgedge/cli/kirk',
  'kirk', 0, 'mqtt.png', 'MQTT Client', 'https://github.com/pgedge/cli/kirk', '');
INSERT INTO releases VALUES ('kirk', 2, 'kirk', 'MQTT Client', '', 'test', '', 1, 'PGEDGE', '', '');
INSERT INTO versions VALUES ('kirk', (select v from hub), '',  1, (select d from hub), '', '', '');

-- ## ACE ##########################
INSERT INTO projects VALUES ('ace', 'pge', 11, 5000, '', 3, 'http://github.com/pgedge/cli/cli/scripts/ace.py',
  'ace',  0, '', 'Anti Chaos Engine for pgEdge', 'https://github.com/pgedge/cli/cli/scripts/ace.py', 'ace');
INSERT INTO releases VALUES ('ace', 2, 'ace',  'ACE', '', 'test', '', 1, 'PGEDGE', '', '');
INSERT INTO versions VALUES ('ace', (select v from hub), '',  1, (select d from hub), '', '', '');

-- ## MINIO #############################
INSERT INTO projects VALUES ('minio', 'app', 11, 9000, '', 4, 'https://github.com/minio/minio/tags',
  'minio', 0, 'minio.png', 'HA', 'https://github.com/minio/minio', '');
INSERT INTO releases VALUES ('minio', 1, 'minio', 'MinIO', '', 'test', '', 1, 'AGPLv3', '', '');
INSERT INTO versions VALUES ('minio', '24.9.13', 'amd, arm', 0, '20240917', '', 'EL', '');

