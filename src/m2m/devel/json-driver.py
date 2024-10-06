import subprocess, sys, os, json


def run_command(p_cmd):
    """Run a command while capturing the live output"""

    cmd = f"{os.getenv('PSX')}/pgedge {p_cmd} --json"
    cmd_l = cmd.split()
    err_kount = 0

    try:
      process = subprocess.Popen(
        cmd_l,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
      )
      while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break

        clean_line = line.decode().strip()

        rc = process_output_line(clean_line, str(cmd_l[1]))
        err_kount = err_kount + rc

    except Exception as e:
        print(f"ERROR: Processing output: {e}")
        return(1)

    if err_kount > 0:
        return(1)

    return(0)


def process_output_line(p_line, p_cmd):
    
  if p_line == "":
      return(0)

  rc = 0
  try:
      jj = json.loads(p_line)
      if p_line.startswith('[{"type": "error",'):
          rc = 1
      elif p_line.startswith('[{"type"'):
          pass
      elif p_cmd in ["info", "list"]:
          ## these data commands pass "funky" json
          pass
      else:
          ## this is a funky line thats ignored (for now)
          pass

  except Exception:
      ## turn it into json info
      out_j = {}
      out_j["type"] = "info"
      out_j["msg"] = p_line
      print(f"[{json.dumps(out_j)}]")
      return(0)

  print(p_line)
  return(rc)


######### MAINLINE ########################
args = sys.argv
arg_len = len(args)
if arg_len != 2:
  print(f"ERROR: invalid args length of {arg_len}")
  sys.exit(1)

cmd = args[1]

rc = run_command(cmd)
print('[{"rc": "' + str(rc) + '"}]')

sys.exit(rc)
