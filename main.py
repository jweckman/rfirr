from rfirr.config import config, device
from rfirr.inside import inside_process
from rfirr.outside import outside_process

# Step 1: In gets weather data and stores it somewhere
# TODO

if device == 'inside_rpi':
    inside_process()
elif device == 'outside_rpi':
    outside_process()
