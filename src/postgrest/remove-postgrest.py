import os
import component, util, startup

comp = "postgrest"
autostart =  util.get_column("autostart", comp)
if autostart == "on":
  startup.stop_linux("postgrest")
  startup.remove_linux("postgrest")

  startup.reload_linux()