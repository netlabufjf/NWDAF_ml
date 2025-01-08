#!/usr/bin/env bash

PCAP_FOLDER=./pcap
OUT_FOLDER=./pcap/output/

PCAP_LIST=$(ls $PCAP_FOLDER | grep .pcap)

# PCAP to JSON and CSV
for i in ${PCAP_LIST[@]}; do
    tshark -r $PCAP_FOLDER$i -T json > $OUT_FOLDER/"$i"_output".json"
    
    tshark -r $PCAP_FOLDER$i -T fields \
    -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.protocol -e frame.len -e _ws.col.info \
    -E header=y -E separator=, -E quote=d -E occurrence=f \
     > $OUT_FOLDER/"$i"_output".csv"

     # To customize the "-e flags" (display filters), see https://www.wireshark.org/docs/dfref/
     # For more information: https://manpages.ubuntu.com/manpages/jammy/man1/tshark.1.html
done
unset PCAP_LIST # clean up after usage

JSON_LIST=$(ls $OUT_FOLDER | grep .json)

# Drop duplicated fields on JSON
for i in ${JSON_LIST[@]}; do
    sed -i '/"ip.addr":/d; /"ip.host":/d' $OUT_FOLDER/$i
done
unset JSON_LIST # clean up after usage
