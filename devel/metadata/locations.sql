DROP VIEW IF EXISTS v_locations;

DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS regions;

DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS geos;
DROP TABLE IF EXISTS providers;

CREATE TABLE providers (
  provider      TEXT     NOT NULL PRIMARY KEY,
  sort_order    SMALLINT NOT NULL,
  short_name    TEXT     NOT NULL,
  disp_name     TEXT     NOT NULL,
  image_file    TEXT     NOT NULL
);
INSERT INTO providers VALUES ('aws',   1, 'AWS',   'Amazon Web Services',   'aws.png');
INSERT INTO providers VALUES ('az',    2, 'Azure', 'Microsoft Azure',       'azure.png');
INSERT INTO providers VALUES ('gcp',   3, 'GCP',   'Google Cloud Platform', 'gcp.png');

CREATE TABLE geos (
  geo    TEXT     NOT NULL,
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
  country3     TEXT     NOT NULL,
  geo          TEXT     NOT NULL REFERENCES geos(geo),
  country_nm   TEXT     NOT NULL
);
INSERT INTO countries VALUES ('us', 'usa', 'na', 'United States');
INSERT INTO countries VALUES ('ca', 'can', 'na', 'Canada');
INSERT INTO countries VALUES ('br', 'bra', 'sa', 'Brazil');
INSERT INTO countries VALUES ('ir', 'irl', 'eu', 'Ireland');
INSERT INTO countries VALUES ('gb', 'gbr', 'eu', 'Great Britain');
INSERT INTO countries VALUES ('de', 'ger', 'eu', 'Germany');
INSERT INTO countries VALUES ('fr', 'fra', 'eu', 'France');
INSERT INTO countries VALUES ('it', 'ita', 'eu', 'Italy');
INSERT INTO countries VALUES ('se', 'swe', 'eu', 'Sweden');
INSERT INTO countries VALUES ('bh', 'bhr', 'me', 'Bahrain');
INSERT INTO countries VALUES ('ae', 'are', 'me', 'UAE');
INSERT INTO countries VALUES ('au', 'aus', 'au', 'Australia');
INSERT INTO countries VALUES ('za', 'zaf', 'af', 'South Africa');
INSERT INTO countries VALUES ('jp', 'jpn', 'ap', 'Japan');
INSERT INTO countries VALUES ('hk', 'hkg', 'ap', 'Hong Kong');
INSERT INTO countries VALUES ('sg', 'sgp', 'ap', 'Singapore');
INSERT INTO countries VALUES ('kr', 'kor', 'ap', 'South Korea');
INSERT INTO countries VALUES ('id', 'idn', 'ap', 'Indonesia');
INSERT INTO countries VALUES ('in', 'ind', 'ap', 'India');
INSERT INTO countries VALUES ('nz', 'nzl', 'ap', 'New Zealand');
INSERT INTO countries VALUES ('cn', 'chn', 'ap', 'China');
INSERT INTO countries VALUES ('es', 'esp', 'eu', 'Spain');
INSERT INTO countries VALUES ('il', 'isr', 'me', 'Israel');
INSERT INTO countries VALUES ('be', 'bel', 'eu', 'Belgium');
INSERT INTO countries VALUES ('nl', 'ned', 'eu', 'Netherlands');
INSERT INTO countries VALUES ('fl', 'fin', 'eu', 'Finland');
INSERT INTO countries VALUES ('tw', 'twn', 'ap', 'Taiwan');
INSERT INTO countries VALUES ('cl', 'chl', 'sa', 'Chile');
INSERT INTO countries VALUES ('pl', 'pol', 'eu', 'Poland');
INSERT INTO countries VALUES ('no', 'nor', 'eu', 'Norway');
INSERT INTO countries VALUES ('qa', 'qat', 'me', 'Qatar');


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


CREATE TABLE regions (
  provider      TEXT       NOT NULL REFERENCES providers(provider),
  location      TEXT       NOT NULL REFERENCES locations(location),
  parent_region TEXT       NOT NULL,
  region        TEXT       NOT NULL,
  avail_zones   TEXT       NOT NULL,
  active_or_comingsoon TEXT  NOT NULL,
  PRIMARY KEY (provider, location)
);
INSERT INTO regions VALUES ('aws', 'iad', 'us-east-1',      'us-east-1',      'a, b, c, d, e, f', 'A');
INSERT INTO regions VALUES ('aws', 'cmh', 'us-east-2',      'us-east-2',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'sfo', 'us-west-1',      'us-west-1',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'pdt', 'us-west-2',      'us-west-2',      'a, b, c, d',       'A');
INSERT INTO regions VALUES ('aws', 'mtl', 'ca-central-1',   'ca-central-1',   'a, b',             'A');
INSERT INTO regions VALUES ('aws', 'sin', 'ap-southeast-1', 'ap-southeast-1', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'icn', 'ap-northeast-2', 'ap-northeast-2', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'hkg', 'ap-east-1',      'ap-east-1',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'itm', 'ap-northeast-3', 'ap-northeast-3', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'nrt', 'ap-northeast-1', 'ap-northeast-1', 'a, b, c, d',       'A');
INSERT INTO regions VALUES ('aws', 'bom', 'ap-south-1',     'ap-south-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'dfw', 'us-east-1',      'us-east-1-dfw-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'den', 'us-west-2',      'us-west-2-den-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'yyc', 'ca-west-1',      'ca-central-1',   'a, b',            'CS');
INSERT INTO regions VALUES ('aws', 'akl', 'ap-southeast-5', 'ap-southeast-5', 'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'cgk', 'ap-southeast-3', 'ap-southeast-3', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'mel', 'ap-southeast-4', 'ap-southeast-4', 'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'syd', 'ap-southeast-2', 'ap-southeast-2', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'hyd', 'ap-south-2',     'ap-south-2',     'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'gru', 'sa-east-1',      'sa-east-1',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'fra', 'eu-central-1',   'eu-central-1',   'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'dub', 'eu-west-1',      'eu-west-1',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'lhr', 'eu-west-2',      'eu-west-2',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'mxp', 'eu-south-1',     'eu-south-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'cdg', 'eu-west-3',      'eu-west-3',      'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'mad', 'eu-east-1',      'eu-east-1',      'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'arn', 'eu-north-1',     'eu-north-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'zrh', 'eu-central-2',   'eu-central-2',   'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'pek', 'cn-north-1',     'cn-north-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'csx', 'cn-northwest-1', 'cn-northwest-1', 'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'cpt', 'af-south-1',     'af-south-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'bah', 'me-south-1',     'me-south-1',     'a, b, c',          'A');
INSERT INTO regions VALUES ('aws', 'tlv', 'me-west-1',      'me-west-1',      'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'auh', 'me-south-2',     'me-south-2',     'a, b, c',         'CS');
INSERT INTO regions VALUES ('aws', 'atl', 'us-east-1',      'us-east-1-atl-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'bos', 'us-east-1',      'us-east-1-bos-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'chi', 'us-east-1',      'us-east-1-chi-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'iah', 'us-east-1',      'us-east-1-iah-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'mci', 'us-east-1',      'us-east-1-mci-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'las', 'us-west-2',      'us-west-2-las-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'lax', 'us-west-2',      'us-west-2-lax-1', 'a, b',            'A');
INSERT INTO regions VALUES ('aws', 'mia', 'us-east-1',      'us-east-1-mia-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'msp', 'us-east-1',      'us-east-1-msp-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'jfk', 'us-east-1',      'us-east-1-nyc-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'phl', 'us-east-1',      'us-east-1-phl-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'phx', 'us-west-2',      'us-west-2-phx-1', 'a',               'A');
INSERT INTO regions VALUES ('aws', 'pdx', 'us-west-2',      'us-west-2-pdx-1', 'a',               'A');

INSERT INTO regions VALUES ('gcp', 'pdt', 'us-west1',                'us-west1',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'lax', 'us-west2',                'us-west2',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'slc', 'us-west3',                'us-west3',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'las', 'us-west4',                'us-west4',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'dsm', 'us-central1',             'us-central1',             'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'chs', 'us-east1',                'us-east1',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'iad', 'us-east4',                'us-east4',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'cmh', 'us-east5',                'us-east5',                'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'dfw', 'us-south1',               'us-south1',               'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'mtl', 'northamerica-northeast1', 'northamerica-northeast1', 'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'yyz', 'northamerica-northeast2', 'northamerica-northeast2', 'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'gru', 'southamerica-east1',      'southamerica-east1',      'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'scl', 'southamerica-west1',      'southamerica-west1',      'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'lhr', 'europe-west2',            'europe-west2',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'bru', 'europe-west1',            'europe-west1',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'ams', 'europe-west4',            'europe-west4',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'zrh', 'europe-west6',            'europe-west6',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'fra', 'europe-west3',            'europe-west3',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'hel', 'europe-north1',           'europe-north1',           'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'waw', 'europe-central2',         'europe-central2',         'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'mil', 'europe-west8',            'europe-west8',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'mad', 'europe-southwest1',       'europe-southwest1',       'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'cdg', 'europe-west9',            'europe-west9',            'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'bom', 'asia-south1',             'asia-south1',             'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'del', 'asia-south2',             'asia-south2',             'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'sin', 'asia-southeast1',         'asia-southeast1',         'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'cgk', 'asia-southeast2',         'asia-southeast2',         'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'hkg', 'asia-east2',              'asia-east2',              'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'tpe', 'asia-east1',              'asia-east1',              'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'nrt', 'asia-northeast1',         'asia-northeast1',         'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'itm', 'asia-northeast2',         'asia-northeast2',         'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'syd', 'australia-southeast1',    'australia-southeast1',    'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'mel', 'australia-southeast2',    'australia-southeast2',    'a, b, c', 'A');
INSERT INTO regions VALUES ('gcp', 'icn', 'asia-northeast3',         'asia-northeast3',         'a, b, c', 'A');

INSERT INTO regions VALUES ('az', 'sea', 'westus2',            'westus2',            'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'lax', 'westus',             'westus',             'a, b, c', 'CS');
INSERT INTO regions VALUES ('az', 'phx', 'westus3',            'westus3',            'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'jac', 'westcentralus',      'westcentralus',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'dsm', 'centralus',          'centralus',          'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'dfw', 'southcentralus',     'southcentralus',     'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'chi', 'northcentralus',     'northcentralus',     'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'iad', 'eastus',             'eastus',             'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'ric', 'eastus2',            'eastus2',            'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'yyz', 'canadacentral',      'canadacentral',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'mtl', 'canadaeast',         'canadaeast',         'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'gru', 'brazilsouth',        'brazilsouth',        'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'jnb', 'southafricanorth',   'southafricanorth',   'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'dub', 'northeurope',        'northeurope',        'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'cwl', 'ukwest',             'ukwest',             'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'lhr', 'uksouth',            'uksouth',            'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'cdg', 'francecentral',      'francecentral',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'arn', 'swedencentral',      'swedencentral',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'osl', 'norwayeast',         'norwayeast',         'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'ams', 'westeurope',         'westeurope',         'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'fra', 'germanywestcentral', 'germanywestcentral', 'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'zrh', 'switzerlandnorth',   'switzerlandnorth',   'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'doh', 'qatarcentral',       'qatarcentral',       'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'auh', 'UAEnorth',           'UAEnorth',           'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'png', 'centralindia',       'centralindia',       'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'maa', 'southindia',         'southindia',         'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'sin', 'southeastasia',      'southeastasia',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'hkg', 'eastasia',           'eastasia',           'a, b, c',  'A');
--INSERT INTO regions VALUES ('az', 'pvg', 'chinaeast',          'chinaeast2',         'a, b, c',  'A');
--INSERT INTO regions VALUES ('az', 'pvg', 'chinaeast',          'chinaeast',          'a, b, c',  'A');
--INSERT INTO regions VALUES ('az', 'pek', 'chinanorth',         'chinanorth2',        'a, b, c',  'A');
--INSERT INTO regions VALUES ('az', 'pek', 'chinanorth',         'chinanorth',         'a, b, c',  'A');
--INSERT INTO regions VALUES ('az', 'pek', 'chinanorth',         'chinanorth3',        'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'icn', 'koreacentral',       'koreacentral',       'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'itm', 'japanwest',          'japanwest',          'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'nrt', 'japaneast',          'japaneast',          'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'syd', 'australiaeast',      'australiaeast',      'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'mel', 'australiasoutheast', 'australiasoutheast', 'a, b, c',  'A');
INSERT INTO regions VALUES ('az', 'cbr', 'australiacentral',   'australiacentral',   'a, b, c',  'A');


CREATE VIEW v_locations AS
SELECT g.geo, c.country3, c.country, l.location, l.state, r.provider, r.region, l.location_nm, 
       l.lattitude, l.longitude, r.parent_region, r.avail_zones
  FROM geos g, countries c, regions r, locations l
 WHERE g.geo = c.geo 
   AND c.country = l.country 
   AND l.location = r.location;

