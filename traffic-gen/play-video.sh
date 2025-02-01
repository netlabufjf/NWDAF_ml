#!/usr/bin/env bash

UE_IP=10.60.0.1 # IP given by 5GC to point-to-point interface (a.k.a. uesimtun0)
YT_URL="https://www.youtube.com/watch?v=LXb3EKWsInQ" # URL of the stored video
NAVER_TV_URL="https://tv.naver.com/l/164367" # URL of the live stream
PREPARE_MODE=0
RUN_MODE=0
LIVE_STREAM=0 # If 1, will use YT_URL, if 0, will use NAVER_TV_URL
USE_FIREFOX=1 # If 1, will use Mozilla Firefox, if 0, will use Brave Browser

# check the input parameters and set the control vars accordingly
if [ $# -gt 0 ]; then
    while [ $# -gt 0 ]; do
        case $1 in
        -prepare)
            PREPARE_MODE=1
            ;;
        -play-yt)
            RUN_MODE=1
            LIVE_STREAM=0
            ;;
        -play-live)
            RUN_MODE=1
            LIVE_STREAM=1
            ;;
        -use-brave)
            if [ $# -gt 1 ]; then
                USE_FIREFOX=0
            else
                echo "[ERRO] The option '-use-brave' can't be used alone"
                exit 1
            fi
            ;;
        *)
            echo "[ERRO] Some input parameter wasn't found. Check your input and try again"
            exit 1
            ;;
        esac
        shift
    done
else
    echo "[ERRO] At least one parameter is required"
    exit 1
fi

check_x_server_availability () {
    # forwarding is necessary to run the browser correctly
    # when connecting remotely
    if [ -n "$DISPLAY" ]; then
        echo "[INFO] X11 forwarding is enabled."
    else
        echo "[ERRO] X11 forwarding is not enabled. Connect to SSH using -X parameter"
        exit 1
    fi
}

prepare () {
    if [[ $USE_FIREFOX -eq 1 ]]; then
        sudo apt install firefox
    elif [[ $USE_FIREFOX -eq 0 ]]; then
        # Install Brave browser instead
        curl -fsS https://dl.brave.com/install.sh | sh 
    fi
}

run () {
    if [ ! -f ./nr-binder ]; then
        echo "[ERRO] nr-binder not found!"
        echo "TIP: move $0 to the same folder as nr-binder"
        # currently this folder is called 'build' on UERANSIM sources
    fi

    # Set URL to be played
    if [[ $LIVE_STREAM -eq 0 ]]; then
        URL=$YT_URL
    elif [[ $LIVE_STREAM -eq 1 ]]; then
        URL=$NAVER_TV_URL
    fi

    if [[ $USE_FIREFOX -eq 1 ]]; then
        bash nr-binder $UE_IP firefox --new-window $URL
    elif [[ $USE_FIREFOX -eq 0 ]]; then
        # Use Brave browser as an alternative
        bash nr-binder $UE_IP brave-browser --new-window --incognito $URL
        # using incognito to prevent Brave resuming a previous session
        # (i.e. 'Continue where you left off')
    fi
}

check_x_server_availability

if [[ $PREPARE_MODE -eq 0 && $RUN_MODE -eq 1 ]]; then
    run
elif [[ $PREPARE_MODE -eq 1 && $RUN_MODE -eq 0 ]]; then
    prepare
elif [[ $PREPARE_MODE -eq 1 && $RUN_MODE -eq 1 ]]; then
    prepare
    run
fi
