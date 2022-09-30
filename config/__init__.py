import atexit
import config.nucleic_acid
from config.panel import panel


# ensure settings saves on exit and loads on entry
config.nucleic_acid.load()
atexit.register(config.nucleic_acid.dump)