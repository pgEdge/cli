 
####################################################################
######          Copyright (c)  2015-2020 BigSQL           ##########
####################################################################

import util

util.change_pgconf_keyval("pgXX", "pljava.libjvm_location", util.get_jvm_location(), True)

util.create_extension("pgXX", "libpljava-so-1.5.5", True, "pljava")

