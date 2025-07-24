#!/usr/bin/env bash

echo -e "[WARN] ALL the data in the output folders will be \033[31mDELETED\033[0m !"
read -p "Press ENTER to continue or Ctrl+C to abort now"

echo -n "[INFO] Removing the output directory ... "
rm -rf ./pcap/output
echo "[ OK ]"

echo -n "[INFO] Reconstructing the output directory structure ... "
mkdir -p ./pcap/output/{1-PCAP-export,2-stats/graphs/,3-JSON-export/box-plots/,4-ML/{preprocess/{labeled_files,labeled_data,data_ready_to_ml,resampled_data},models/training_results,inference_results}}
echo "[ OK ]"
