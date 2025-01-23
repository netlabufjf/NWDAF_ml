#!/usr/bin/env bash

echo -e "[WARN] ALL the data in the output folders will be \033[31mDELETED\033[0m !"
read -p "Press ENTER to continue or Ctrl+C to abort now"

echo "[INFO] Removing the output directory"
rm -rf ./pcap/output

echo "[INFO] Reconstructing the output directory structure"
mkdir -p ./pcap/output/{1-PCAP-export,2-stats/graphs/,3-JSON-export}
echo "[INFO] Done"
