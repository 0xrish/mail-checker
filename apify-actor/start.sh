#!/bin/bash

# Start chromedriver in the background
# Port 9515 is the default for reacher-cli
chromedriver --port=9515 --whitelisted-ips= &

# Wait a moment for chromedriver to start
sleep 2

# Run the Python actor
python3 -m main
