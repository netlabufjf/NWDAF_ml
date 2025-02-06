#!/usr/bin/env bash

TRAINING_PCAP_FOLDER=./pcap/input/training_data/ # read training raw PCAP files from here
INFERENCE_PCAP_FOLDER=./pcap/input/inference_data/ # read inference raw PCAP files from here
OUT_FOLDER=./pcap/output/1-PCAP-export/ # save the output there

# set IFS to break only on new line (so the input files can have white space on their names)
# for more info: https://www.linuxquestions.org/questions/programming-9/bash-put-output-from-%60ls%60-into-an-array-346719/#post1765355
IFS='
'

TRAINING_PCAP_LIST=("$TRAINING_PCAP_FOLDER"*.pcap)
INFERENCE_PCAP_LIST=("$INFERENCE_PCAP_FOLDER"*.pcap)

# Check if folder is empty, if yes, delete the related var to avoid "file not found" errors
if [[ "$TRAINING_PCAP_LIST" == *"*"* ]]; then
    # TRAINING_PCAP_LIST=""
    unset TRAINING_PCAP_LIST
elif [[ "$INFERENCE_PCAP_LIST" == *"*"* ]]; then
    # INFERENCE_PCAP_LIST=""
    unset INFERENCE_PCAP_LIST
fi

# Then calculate these sizes after that
TRAINING_PCAP_LIST_SIZE=${#TRAINING_PCAP_LIST[@]}
INFERENCE_PCAP_LIST_SIZE=${#INFERENCE_PCAP_LIST[@]}
TOTAL_LIST_SIZE=$((TRAINING_PCAP_LIST_SIZE + INFERENCE_PCAP_LIST_SIZE))

# TIME_START=$(date +%s) # record start time

# PCAP to JSON and CSV
extract_JSON_and_CSV () {
    local FILE_NAME=$1
    local PCAP_FOLDER=$2
    local OUT_FOLDER=$3
    local SET_SPLIT_TAG=$4

    echo "[INFO] Extracting data from $FILE_NAME"

    tshark -r $PCAP_FOLDER$FILE_NAME -T json > $OUT_FOLDER/"${FILE_NAME%.*}_$SET_SPLIT_TAG.json" && \
    tshark -r $PCAP_FOLDER$FILE_NAME -T fields \
    -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.protocol -e frame.len -e _ws.col.info \
    -E header=y -E separator=, -E quote=d -E occurrence=f \
    > $OUT_FOLDER/"${FILE_NAME%.*}_$SET_SPLIT_TAG.csv"
    # To customize the "-e flags" (display filters), see https://www.wireshark.org/docs/dfref/
    # For more information: https://manpages.ubuntu.com/manpages/jammy/man1/tshark.1.html
}

# JSON field remover
field_remover () {
    local FILE_NAME=$1
    local OUT_FOLDER=$2

    echo "[INFO] Removing duplicated fields from $FILE_NAME"

    sed -i '/"ip.addr":/d; /"ip.host":/d ; /"udp.port":/d' $OUT_FOLDER$FILE_NAME
}

time { # track execution time
echo "[INFO] Exporting $TRAINING_PCAP_LIST_SIZE training and $INFERENCE_PCAP_LIST_SIZE inference PCAP files"
if [ $TRAINING_PCAP_LIST_SIZE -ne 0 ]; then
    for i in "${TRAINING_PCAP_LIST[@]}"; do
        extract_JSON_and_CSV "${i##*/}" $TRAINING_PCAP_FOLDER $OUT_FOLDER "training" &
    done
fi
if [ $INFERENCE_PCAP_LIST_SIZE -ne 0 ]; then
    for j in "${INFERENCE_PCAP_LIST[@]}"; do
        extract_JSON_and_CSV "${j##*/}" $INFERENCE_PCAP_FOLDER $OUT_FOLDER "inference" &
    done
fi
wait
unset TRAINING_PCAP_LIST # clean up after usage
unset INFERENCE_PCAP_LIST_SIZE # clean up after usage
echo "[INFO] All $TOTAL_LIST_SIZE files have been successfully exported"

JSON_LIST=("$OUT_FOLDER"*.json)
JSON_LIST_SIZE=${#JSON_LIST[@]}

# Drop duplicated fields on JSON
echo "[INFO] Removing duplicated entries from $JSON_LIST_SIZE JSON files"
if [ $JSON_LIST_SIZE -ne 0 ]; then
    for i in "${JSON_LIST[@]}"; do
        field_remover "${i##*/}" $OUT_FOLDER &
    done
else
    echo "[ERRO] No JSON files found in the directory: $OUT_FOLDER"
    exit 1
fi
wait
unset JSON_LIST # clean up after usage
echo "[INFO] All $TOTAL_LIST_SIZE files have been processed"

echo "[DEBUG] Execution time:"
}

# TIME_END=$(date +%s) # record end time
# echo "[DEBUG] Execution time: $((TIME_END-TIME_START)) seconds"
