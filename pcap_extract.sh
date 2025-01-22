#!/usr/bin/env bash

PCAP_FOLDER=./pcap/input/ # read raw PCAP files from here
OUT_FOLDER=./pcap/output/1-PCAP-export/ # save the output there

# set IFS to break only on new line (so the input files can have white space on their names)
# for more info: https://www.linuxquestions.org/questions/programming-9/bash-put-output-from-%60ls%60-into-an-array-346719/#post1765355
IFS='
'

PCAP_LIST=$(ls $PCAP_FOLDER | grep .pcap)
COUNTER=0
PCAP_LIST_SIZE=$(wc -l <<< "$PCAP_LIST")

# TIME_START=$(date +%s) # record start time

# PCAP to JSON and CSV
time { # track execution time
echo "[INFO] Exporting $PCAP_LIST_SIZE PCAP files"
for i in ${PCAP_LIST[@]}; do
    tshark -r $PCAP_FOLDER$i -T json > $OUT_FOLDER/"${i%.*}.json" && \
    tshark -r $PCAP_FOLDER$i -T fields \
    -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.protocol -e frame.len -e _ws.col.info \
    -E header=y -E separator=, -E quote=d -E occurrence=f \
     > $OUT_FOLDER/"${i%.*}.csv" &

     # To customize the "-e flags" (display filters), see https://www.wireshark.org/docs/dfref/
     # For more information: https://manpages.ubuntu.com/manpages/jammy/man1/tshark.1.html

    ((COUNTER+=1))
    PROGRESS=$(bc <<< "scale=2;$COUNTER*100/$PCAP_LIST_SIZE")
    echo "[INFO] Status: $COUNTER of $PCAP_LIST_SIZE ($PROGRESS %)"
done
wait
unset PCAP_LIST # clean up after usage

JSON_LIST=$(ls $OUT_FOLDER | grep .json)
JSON_LIST_SIZE=$(wc -l <<< "$JSON_LIST")
COUNTER=0

# Drop duplicated fields on JSON
echo "[INFO] Removing JSON duplicated entries"
for i in ${JSON_LIST[@]}; do
    sed -i '/"ip.addr":/d; /"ip.host":/d ; /"udp.port":/d' $OUT_FOLDER/$i &

    ((COUNTER+=1))
    PROGRESS=$(bc <<< "scale=2;$COUNTER*100/$JSON_LIST_SIZE")
    echo "[INFO] Status: $COUNTER of $JSON_LIST_SIZE ($PROGRESS %)"
done
wait
unset JSON_LIST # clean up after usage

echo "[DEBUG] Execution time:"
}

# TIME_END=$(date +%s) # record end time
# echo "[DEBUG] Execution time: $((TIME_END-TIME_START)) seconds"
