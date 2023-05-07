from threading import Thread
from jsonrpcserver import serve

from rfirr.config import config, DeviceType
from rfirr.inside import inside_process
from rfirr.outside import outside_process
from rfirr.scheduling import schedule_daemon

# TODO
# Step 1: In gets weather data and stores it somewhere

# RPC mode starts an rpc server. Intended to be used as 24/7 running service that
# can be called to do things as needed. Much more simple but can only be used
# if the outside process has access to power
# Runs the self-made schedule_daemon on a separate thread 
# due to rpc server taking control.
if config.mode == 'rpc':
    scheduling_thread = Thread(target = schedule_daemon)
    scheduling_thread.start()
    serve('0.0.0.0', 5001)

# Dual rf mode is the original mode using radio frequencies to start 
# the outside rpi using the an inside machine. Better suited for
# battery constrained situations
elif config.mode == "dual_rf":
    if config.device == DeviceType.INSIDE_RPI:
        inside_process()
    elif config.device == DeviceType.OUTSIDE_RPI:
        outside_process(do_shutdown=True)
