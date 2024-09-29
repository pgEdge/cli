
import util

m2m_pidfile = f"{util.getreqenv('MY_DATA')}/m2m.pid"
util.set_column("pidfile", "m2m", m2m_pidfile)
