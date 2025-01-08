#!/usr/bin/env bash

PCAP_FOLDER=./pcap/input/
OUT_FOLDER=./pcap/output/

PCAP_LIST=$(ls $PCAP_FOLDER | grep .pcap)
COUNTER=0
PCAP_LIST_SIZE=$(wc -w <<< "$PCAP_LIST")

# TIME_START=$(date +%s) # record start time

# PCAP to JSON and CSV
time { # track execution time
echo "[INFO] Exporting PCAP files"
for i in ${PCAP_LIST[@]}; do
    tshark -r $PCAP_FOLDER$i -T json > $OUT_FOLDER/"${i%.*}.json"
    
    tshark -r $PCAP_FOLDER$i -T fields \
    -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.protocol -e frame.len -e _ws.col.info \
    -E header=y -E separator=, -E quote=d -E occurrence=f \
     > $OUT_FOLDER/"${i%.*}.csv"

     # To customize the "-e flags" (display filters), see https://www.wireshark.org/docs/dfref/
     # For more information: https://manpages.ubuntu.com/manpages/jammy/man1/tshark.1.html

    ((COUNTER+=1))
    PROGRESS=$(bc <<< "scale=2;$COUNTER*100/$PCAP_LIST_SIZE")
    echo "[INFO] Status: $COUNTER of $PCAP_LIST_SIZE ($PROGRESS %)"
done
unset PCAP_LIST # clean up after usage

JSON_LIST=$(ls $OUT_FOLDER | grep .json)
JSON_LIST_SIZE=$(wc -w <<< "$JSON_LIST")
COUNTER=0

# Drop duplicated fields on JSON
echo "[INFO] Removing JSON duplicated entries"
for i in ${JSON_LIST[@]}; do
    sed -i '/"ip.addr":/d; /"ip.host":/d' $OUT_FOLDER/$i

    ((COUNTER+=1))
    PROGRESS=$(bc <<< "scale=2;$COUNTER*100/$JSON_LIST_SIZE")
    echo "[INFO] Status: $COUNTER of $JSON_LIST_SIZE ($PROGRESS %)"
done
unset JSON_LIST # clean up after usage

echo "[DEBUG] Execution time:"
}

# TIME_END=$(date +%s) # record end time
# echo "[DEBUG] Execution time: $((TIME_END-TIME_START)) seconds"
