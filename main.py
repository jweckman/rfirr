from rfirr.config import config, device
from rfirr.inside import inside_process
from rfirr.outside import outside_process
from jsonrpcserver import serve

mode = config['common']['mode']

# TODO
# Step 1: In gets weather data and stores it somewhere

# RPC mode starts an rpc server. Intended to be used as 24/7 running service that
# can be called to do things as needed. Much more simple but can only be used
# if the outside process has access to power
if mode == 'rpc':
    serve('0.0.0.0', 5001)

# Dual rf mode is the original mode using radio frequencies to start 
# the outside rpi using the an inside machine. Better suited for
# battery constrained situations
elif mode == "dual_rf":
    if device == 'inside_rpi':
        inside_process()
    elif device == 'outside_rpi':
        outside_process(do_shutdown=True)
