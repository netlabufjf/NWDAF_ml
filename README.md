# NWDAF ML

## Tested Environment Configuration

### Software

- python: 3.13.1
- pip: 24.3.1
- tshark: 4.4.2

**NOTE:** List updated on January, 2025

### Hardware

TODO

### Quick comparison between [Kim et al. 2022], our previous work and current work

TODO Update this section

The authors of [[Kim et al. 2022]](https://doi.org/10.1109/ICCE53296.2022.9730290) implemented the NWDAF module and its submodules (MTLF and AnLF) integrated to free5GC, however, they used an image dataset as their ML functionality.

First, a reprodction of [Kim et al. 2022]'s work was made (this README details the environment used in this process). After that, [another ML functionality](./ML_test_code/) closely related to Computer Networks field was implemented. Instead of using an image dataset, a [packet capture dataset](https://github.com/oliveiraleo/mnc_NWDAF/tree/mnc_Public-5G/ML_test_code/dataset) containing 6 captures of 1000 packets each was created. This dataset was used to test the new ML functionality and the instructions to reproduce the environment used for this second phase are located on [this other file here](./VMs-setup.md). 

Currently, the integration between [Kim et al. 2022]'s NWDAF and our ML functionality isn't finished yet, so Keras and TesorFlow are not being used on our experiment.

## Install the prerequisites

**NOTE:** In this section the commands are supported on a BASH console

1. Clone the repo
```
git clone https://github.com/netlabufjf/NWDAF_ml.git
```

2. Install Python3 and pip and configure a virtual environment
```
sudo apt install python3 python3-pip python3-venv
cd NWDAF_ml # enter to repository's root folder
python -m venv pyvenv
source pyvenv/bin/activate
```

3. Install Python required packages
```
pip install -r requirements.txt
```

## Usage

1. Go to the root folder and activate the virtual environment
```
cd NWDAF_ml # enter to repository's root folder
source pyvenv/bin/activate
```

2. TODO

TODO

## Citing this work

TBD

## License

The original code from upstream did not explicitly specify any license terms. However, the [work contained in this repository](https://github.com/net-ty/mnc_NWDAF/compare/mnc_Public-5G...netlabufjf:NWDAF_ml:ml) is licensed under the GPLv3, as indicated in the [LICENSE](./LICENSE) file, which is reflected in the notice provided below:

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For the json2csv [submodule license](./pcap_json2csv/LICENSE), check [its own notice](./pcap_json2csv/README.md#license).
