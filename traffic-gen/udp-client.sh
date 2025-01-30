#!/usr/bin/env bash

# Basic UDP client

# SLEEP_TIMER=60 # send packets in a fixed rate
IP_UE=10.60.0.1
IP_5GC=10.0.0.110
DEST_PORT=30000 # port used to connect to server
SOURCE_PORT=1337 # port used to send the packets

while true; do
    SLEEP_TIMER=$((1 + RANDOM % 20)) # send packets in the interval between 1 to 20 seconds
    # the interval above was taken from https://doi.org/10.1109/INFCOMW.2017.8116438
    LOAD_ONE_MIN=$(cat /proc/loadavg | awk '{print $1}')
    echo "[INFO] Sending data"
    echo -e "System Load: $LOAD_ONE_MIN Next update in $SLEEP_TIMER seconds" | nc -4 -u -w0 -s $IP_UE $IP_5GC $DEST_PORT -p $SOURCE_PORT # nc client
    echo "[INFO] Sleeping for $SLEEP_TIMER seconds..."
    sleep $SLEEP_TIMER
done
