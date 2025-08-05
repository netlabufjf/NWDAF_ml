#!/usr/bin/env bash

time { # track execution time
bash pcap_extract.sh
python dataset_CSV_characterization.py
python stat-plotter.py


python export_JSON.py
python box-plotter.py
bash add_label_to_name.sh

python ml.py

python inference.py

echo "[DEBU] Execution time:"
}