"""Small independent resource snapshot used by replay and supervisor, unprivileged."""
from stage3.monitor import Monitor
monitor=Monitor()
def sample_host():return monitor.sample()
