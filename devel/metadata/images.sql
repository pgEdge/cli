
DROP VIEW  IF EXISTS v_images;
DROP TABLE IF EXISTS flavors;
DROP TABLE IF EXISTS images;

CREATE TABLE images (
  os                 TEXT  NOT NULL,
  platform           TEXT  NOT NULL,
  provider           TEXT  NOT NULL,
  region             TEXT  NOT NULL,
  image_id           TEXT  NOT NULL,
  PRIMARY KEY (os, platform, provider, region)
);

INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'us-east-2',      'ami-0efb26624e3465a3f');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'us-east-1',      'ami-09243ba0df36156d9');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'us-west-1',      'ami-05ddb2c6c5af83038');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'us-west-2',      'ami-03c611a7139a5fb3d');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'af-south-1',     'ami-0eed8584ea715b9ca');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-east-1',      'ami-019ace0ca713bd120');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-south-1',     'ami-0943603e22819c718');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-northeast-1', 'ami-04faacd6a54412896');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-northeast-2', 'ami-018912c905c087bbd');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-southeast-1', 'ami-06dcc555ddfc2f735');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ap-southeast-2', 'ami-0ae3420fe1e837f9c');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'ca-central-1',   'ami-05343c8a47bdd7aac');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-central-1',   'ami-0b227c6aa1ee894c7');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-west-1',      'ami-0abb61cf5e7190a62');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-west-2',      'ami-03ab419be154d7234');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-west-3',      'ami-01fd5c10205501702');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-south-1',     'ami-09ca6473e02894a46');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'eu-north-1',     'ami-04a86dd9bcd579a84');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'me-south-1',     'ami-02d75b05b991c759c');
INSERT INTO images VALUES ('cos8', 'arm', 'aws', 'sa-east-1',      'ami-051a6f18b3af1792d');

INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'af-south-1',     'ami-01b703fbb001d2dae');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-east-1',      'ami-0932c85be19891d3e');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-northeast-1', 'ami-0be7fb7ee5cff3b58');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-northeast-2', 'ami-02a8e74d508493718');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-northeast-3', 'ami-02079f0285e75a8be');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-south-1',     'ami-0c66c4f14d217d16f');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-southeast-1', 'ami-0d43b5bf95246b21e');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-southeast-2', 'ami-08bd9ec03d33ea2d0');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ap-southeast-3', 'ami-0f56e7c4be5859a54');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'ca-central-1',   'ami-04098e83837a4d344');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-central-1',   'ami-05d8c3dc27d413c4b');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-north-1',     'ami-0a59b7c4604a5398f');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-south-1',     'ami-02d63f90e4e82e824');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-west-1',      'ami-0aeaee482a16c861d');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-west-2',      'ami-018542fa4c710a021');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'eu-west-3',      'ami-03fd6adde045f50ea');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'me-central-1',   'ami-0dd81b9d6625dddef');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'me-south-1',     'ami-086b910f354e11b9d');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'sa-east-1',      'ami-0b9adf9ed18361f50');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'us-east-1',      'ami-0f69dd1d0d03ad669');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'us-east-2',      'ami-0a9790c5a531163ee');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'us-west-1',      'ami-0ccc14818d8c254d6');
INSERT INTO images VALUES ('ubu22', 'arm', 'aws', 'us-west-2',      'ami-0db84aebfa8d17e23');


CREATE VIEW v_images AS
SELECT l.geo, l.country, l.location, l.provider, l.region, l.location_nm, 
       l.lattitude, l.longitude, l.parent_region, l.avail_zones, i.os, i.platform, i.image_id
  FROM v_locations l, images i
 WHERE l.provider = i.provider
   AND l.parent_region = i.region;


CREATE TABLE flavors (
  provider      TEXT     NOT NULL REFERENCES providers(provider),
  flavor        TEXT     NOT NULL,
  size          TEXT     NOT NULL,
  v_cpu         INTEGER  NOT NULL,
  mem_gb        INTEGER  NOT NULL,
  das_gb        FLOAT    NOT NULL,
  network_gbps  TEXT     NOT NULL,
  PRIMARY KEY (provider, flavor)
);
INSERT INTO flavors VALUES ('aws', 'm',    'r6gd.medium',        1,   8,    59, 'Up to 10');
INSERT INTO flavors VALUES ('aws', 'l',    'r6gd.large',         2,  16,   118, 'Up to 10');
INSERT INTO flavors VALUES ('aws', 'xl',   'r6gd.xlarge',        4,  32,   237, 'Up to 10');
INSERT INTO flavors VALUES ('aws', '2xl',  'r6gd.2xlarge',       8,  64,   474, 'Up to 10');
INSERT INTO flavors VALUES ('aws', '4xl',  'r6gd.4xlarge',      16, 128,   950, 'Up to 10');
INSERT INTO flavors VALUES ('aws', '8xl',  'r6gd.8xlarge',      32, 256,  1900, '12');
INSERT INTO flavors VALUES ('aws', '12xl', 'r6gd.12xlarge',     48, 384,  2850, '20');
INSERT INTO flavors VALUES ('aws', '16xl', 'r6gd.16xlarge',     64, 512,  3800, '25');
INSERT INTO flavors VALUES ('az',  '2xl',  'Standard_L8s_v2',    8,  64,  1.92, '3.2');
INSERT INTO flavors VALUES ('az',  '4xl',  'Standard_L16s_v2',  16, 128,  3.84, '6.4');
INSERT INTO flavors VALUES ('az',  '8xl',  'Standard_L32s_v2',  32, 256,  7.68, '12.8');
INSERT INTO flavors VALUES ('az',  '12xl', 'Standard_L48s_v2',  48, 384, 11.52, '16+');
INSERT INTO flavors VALUES ('az',  '16xl', 'Standard_L64s_v2',  64, 512, 15.36, '16+');
INSERT INTO flavors VALUES ('az',  '20xl', 'Standard_L80s_v2',  80, 640, 19.20, '16+');
