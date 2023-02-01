import os

import util

if os.getenv("isAutoStart", "") == "True":
  os.system("./nc init bouncer")
  os.system("./nc start bouncer")

