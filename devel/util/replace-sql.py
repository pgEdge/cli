import os

for subdir, dirs, files in os.walk('./'):
  for orig_file in files:
    if orig_file.endswith(".sql"):
      full_file = subdir + "/" + orig_file
      print(full_file)
      with open (full_file, 'r') as source_content:
        src = source_content.read()
        src = src.replace("pglogical", "pgspock")
        src = src.replace("PGLogical", "PGSpock")
        src = src.replace("Copyright", "Portions Copyright")
        src = src.replace("PGLOGICAL", "PGSPOCK")
        src = src.replace("PGL", "PGS")
        src = src.replace("PG_LOGICAL", "PG_SPOCK")
        src = src.replace("PGlogical", "PGspock")
        src = src.replace("pgl_", "pgs_")
        with open (full_file, 'w') as f:
          f.write(src)
        #print(src)
        #print("")
