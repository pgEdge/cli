import os

for subdir, dirs, files in os.walk('./'):
  for orig_file in files:
    if orig_file.startswith("pglogical_") and (orig_file.endswith(".c") or orig_file.endswith(".h")):
      new_file = subdir + "/" + orig_file.replace("pglogical_", "pgspock_")
      print(subdir + "/" + orig_file + " --> " + new_file)
      os.system("cp " + subdir + "/" + orig_file + "  " + new_file)
