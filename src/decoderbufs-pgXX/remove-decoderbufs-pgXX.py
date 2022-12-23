 
####################################################################
######          Copyright (c)  2020-2021 OpenRDS          ##########
####################################################################

import util

util.remove_pgconf_keyval("pgXX", "shared_preload_libraries", "decoderbufs")

