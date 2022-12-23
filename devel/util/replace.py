import os

for subdir, dirs, files in os.walk('./'):
  for orig_file in files:
    if orig_file.startswith("spock_") and (orig_file.endswith(".c") or orig_file.endswith(".h")):
      full_file = subdir + "/" + orig_file
      print(full_file)
      with open (full_file, 'r') as source_content:
        src = source_content.read()
        src = src.replace("pglogical", "spock")
        src = src.replace("PGLogical", "Spock")
        src = src.replace("PGLOGICAL", "SPOCK")
        src = src.replace("PGL", "SPK")
        src = src.replace("PG_LOGICAL", "SPOCK")
        src = src.replace("PGlogical", "Spock")
        src = src.replace("pgl_", "spk_")
        with open (full_file, 'w') as f:
          f.write(src)
        #print(src)
        #print("")
