# nodectl/Makefile

PGFILEDESC = "nodectl - manage instances"

# PROGRAM = dummy
OBJS = dummy.o

TAP_TESTS = 1

USE_PGXS=1

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
