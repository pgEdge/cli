
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

CREATE VIEW v_images AS
SELECT l.geo, l.country, l.location, l.provider, l.region, l.location_nm, 
       l.lattitude, l.longitude, l.parent_region, l.avail_zones, i.os, i.platform, i.image_id
  FROM v_locations l, images i
 WHERE l.provider = i.provider
   AND l.parent_region = i.region;


CREATE TABLE flavors (
  provider      TEXT     NOT NULL REFERENCES providers(provider),
  flavor        TEXT     NOT NULL,
  price_hr      NUMERIC(6,3) NOT NULL,
  size          TEXT     NOT NULL,
  v_cpu         INTEGER  NOT NULL,
  mem_gb        INTEGER  NOT NULL,
  das_gb        FLOAT    NOT NULL,
  comment       TEXT,
  PRIMARY KEY (provider, flavor)
);
INSERT INTO flavors VALUES ('aws', 'm',    0.0452, 'm6gd.medium',        1,   4,    59, '1 x 59');
INSERT INTO flavors VALUES ('aws', 'l',    0.0904, 'm6gd.large',         2,   8,   118, '1 x 118 ');
INSERT INTO flavors VALUES ('aws', 'xl',   0.1808, 'm6gd.xlarge',        4,  16,   237, '1 x 237');
INSERT INTO flavors VALUES ('aws', '2xl',  0.3616, 'm6gd.2xlarge',       8,  32,   474, '1 X 474');
INSERT INTO flavors VALUES ('aws', '4xl',  0.7232, 'm6gd.4xlarge',      16,  64,   950, '1 x 950');
INSERT INTO flavors VALUES ('aws', '8xl',  1.4464, 'm6gd.8xlarge',      32, 128,  1900, '12');
INSERT INTO flavors VALUES ('aws', '12xl', 2.1696, 'm6gd.12xlarge',     48, 192,  2850, '2 x 1425 NVMe SSD');
INSERT INTO flavors VALUES ('aws', '16xl', 2.8928, 'm6gd.16xlarge',     64, 256,  3800, '2 x 1900 NVMe SSD');
INSERT INTO flavors VALUES ('az',  '2xl',       0, 'Standard_L8s_v2',    8,  64,  1.92, '3.2');
INSERT INTO flavors VALUES ('az',  '4xl',       0, 'Standard_L16s_v2',  16, 128,  3.84, '6.4');
INSERT INTO flavors VALUES ('az',  '8xl',       0, 'Standard_L32s_v2',  32, 256,  7.68, '12.8');
INSERT INTO flavors VALUES ('az',  '12xl',      0, 'Standard_L48s_v2',  48, 384, 11.52, '16+');
INSERT INTO flavors VALUES ('az',  '16xl',      0, 'Standard_L64s_v2',  64, 512, 15.36, '16+');
INSERT INTO flavors VALUES ('az',  '20xl',      0, 'Standard_L80s_v2',  80, 640, 19.20, '16+');
