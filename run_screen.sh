#!/bin/bash
# This script is what you want to run at startup. It spawns a screen instance (need to install screen)
# and does everything there. You can easily access it by typing "screen -S" in your terminal

# Activate screen if is not already activated
if [ -z "$STY" ]; then exec screen -dm -S screenName /bin/bash "$0"; fi

# Get script directory 
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $DIR

# Run the app. If it fails here, your poetry is probably installed elsewhere. Find it and change
/home/pi/.local/bin/poetry run python3 -m main
