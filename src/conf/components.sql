
DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
  section            TEXT      NOT NULL,
  s_key              TEXT      NOT NULL,
  s_value            TEXT      NOT NULL,
  PRIMARY KEY (section, s_key)
);
INSERT INTO settings VALUES ('GLOBAL', 'REPO', 'https://oscg-io-download.s3.amazonaws.com/REPO');


DROP TABLE IF EXISTS hosts;
CREATE TABLE hosts (
  host_id            INTEGER   PRIMARY KEY,
  host               TEXT      NOT NULL,
  name               TEXT,
  last_update_utc    DATETIME,
  unique_id          TEXT
);
INSERT INTO hosts (host) VALUES ('localhost');


DROP TABLE IF EXISTS components;
CREATE TABLE components (
  component          TEXT     NOT NULL PRIMARY KEY,
  project            TEXT     NOT NULL,
  version            TEXT     NOT NULL,
  platform           TEXT     NOT NULL,
  port               INTEGER  NOT NULL,
  status             TEXT     NOT NULL,
  install_dt         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  autostart          TEXT,
  datadir            TEXT,
  logdir             TEXT,
  pidfile            TEXT,
  svcname            TEXT,
  svcuser            TEXT
);


DROP TABLE IF EXISTS volumes;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS clouds;
DROP TABLE IF EXISTS keys;
DROP TABLE IF EXISTS clusters;
