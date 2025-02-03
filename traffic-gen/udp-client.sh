#!/usr/bin/env bash

# Basic UDP client

# SLEEP_TIMER=60 # send packets in a fixed rate (1 packet/sec)
# SLEEP_TIMER=0.01 # send packets in a fixed rate (100 packets/sec)
IP_UE=10.60.0.1
IP_5GC=10.0.0.110
DEST_PORT=30000 # port used to connect to server
SOURCE_PORT=1337 # port used to send the packets

get_sleep_time(){
    # Generate a random number from 0 to 100
    num=$(shuf -i 0-100 -n 1)

    # Determine which range the number falls into based on the probabilities
    # the intervals below were based on https://doi.org/10.1109/INFCOMW.2017.8116438 (page 3)
    if [ $num -lt 85 ]; then # 0-20 range (85% probability)
            min=1
            max=20
    elif [ $num -lt 96 ]; then # 20-60 range (11% probability)
            min=20
            max=60
    else # 60-90 range (the 4% probability left)
            min=60
            max=90
            # NOTE source above doesn't specify a upper limit
            # it only says "longer than one minute"
            # so I decided to limit to 90s
    fi

    raffle=$((min + RANDOM % (max - min + 1)))

    # echo "[DEBU] Value: $raffle"
    echo "$raffle"
}

while true; do
    # SLEEP_TIMER=$((1 + RANDOM % 20)) # send packets in the interval between 1 to 20 seconds
    SLEEP_TIMER=$(get_sleep_time) # send packets in the interval between 1 to 90 seconds with probabilities
    LOAD_ONE_MIN=$(cat /proc/loadavg | awk '{print $1}')
    echo "[INFO] Sending data"
    echo -e "System Load: $LOAD_ONE_MIN Next update in $SLEEP_TIMER seconds" | nc -4 -u -w0 -s $IP_UE $IP_5GC $DEST_PORT -p $SOURCE_PORT # nc client
    echo "[INFO] Sleeping for $SLEEP_TIMER seconds..."
    sleep $SLEEP_TIMER
done
