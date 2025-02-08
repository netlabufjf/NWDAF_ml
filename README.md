# NWDAF ML

## Tested Environment Configuration

### Software

- python: 3.13.1
- pip: 24.3.1
- python packages from [requirements.txt](./requirements.txt)
- tshark: 4.4.2
- perl: 5.40.0

### Hardware

The hardware specifications below concern the Machine Learning (ML) experiment pipeline (e.g. processing the dataset, training models and running inference). For the hardware and software requirements for generating a new 5G simulated traffic dataset, please, refer to [the traffic-gen README file](./traffic-gen/README.md).

#### Minimum

- 4x 3.0GHz CPU cores
- 16GB of RAM
- `A`GB HDD to store the input dataset
- ~11.3x`A` HDD available to store the temporary files of preprocessed data
- ~2x`A` HDD to store the preprocessed data

**TIP:** The dataset we tested had 19.6GB training + 2.4GB inference data (i.e. `A = 22GB`), see the values on the list [below](./README.md#recommended)

#### Recommended

The specifications below were taken from the machine used during the experiments. If you don't have this amount of resources, consider downloading the preprocessed files or splitting the data to be processed in blocks (specially on `pcap_extract.sh` and `export_JSON.py` steps, that require the largest amount of HDD and RAM).

- 16x 3.8GHz CPU cores
- 4x 32GB of RAM 3200MT/s CL16
- 128GB SWAP (not needed if 256GB of RAM is available)
- 25GB SSD 5000MB/s write / 3200MB/s read* to store the input dataset
- 400GB SSD available to store the temporary files of preprocessed data
- 50GB SSD to store the preprocessed data

\* A 450MB/s SATA interface might be enough

**NOTE:** These specifications are tailored to the datasets we tested on our implementation. The amount of RAM required increases linearly with the size of the dataset as the dataset will be loaded into RAM during training. The amount of CPU cores available will directly influence the parallel tasks (such as in `pcap_extract.sh` and `export_JSON.py`), the more input files, the more CPUs are required.

### Quick comparison between [Kim et al. 2022], our previous work and current work

TODO Update this section

The authors of [[Kim et al. 2022]](https://doi.org/10.1109/ICCE53296.2022.9730290) implemented the NWDAF module and its submodules (MTLF and AnLF) integrated to free5GC, however, they used an image dataset as their ML functionality.

First, a reprodction of [Kim et al. 2022]'s work was made (this README details the environment used in this process). After that, [another ML functionality](./ML_test_code/) closely related to Computer Networks field was implemented. Instead of using an image dataset, a [packet capture dataset](https://github.com/oliveiraleo/mnc_NWDAF/tree/mnc_Public-5G/ML_test_code/dataset) containing 6 captures of 1000 packets each was created. This dataset was used to test the new ML functionality and the instructions to reproduce the environment used for this second phase are located on [this other file here](./VMs-setup.md). 

Currently, the integration between [Kim et al. 2022]'s NWDAF and our ML functionality isn't finished yet, so Keras and TesorFlow are not being used on our experiment.

## Install the prerequisites

**NOTE:** In this section the commands are supported on a BASH console

1. Clone the repo
```
git clone https://github.com/netlabufjf/nwdaf_ml.git
```

2. Install Python3 and pip and configure a virtual environment
```
sudo apt install python3 python3-pip python3-venv
cd nwdaf_ml # enter to repository's root folder
python -m venv pyvenv
source pyvenv/bin/activate
```

3. Install Python required packages
```
pip install -r requirements.txt
```

4. Install Perl and Perl JSON module

Example:
```
sudo apt install perl
cpan install JSON
```

## Usage

1. Go to the root folder and activate the virtual environment
```
cd nwdaf_ml # enter to repository's root folder
source pyvenv/bin/activate
```

2. Move the input PCAP files to ./pcap/input or edit the path in the scripts

3. Execute the steps to extract the PCAP data and obtain some statistics
```
bash pcap_extract.sh
python dataset_CSV_characterization.py

```

4. Prepare the dataset for model training
```
python export_JSON.py
bash add_label_to_name.sh
```

5. Execute the Machine Learning script to preprocess the data and train the models
```
python ml.py
```

6. Execute the inference using the trained models
```
python inference.py
```

### Statistics

1. To obtain some statistics, run steps 1-3 from [previous section](#usage) and:
```
python stat-plotter.py
```

2. To obtain some more statistics (box plots), run up to the first command of step 4 from the [previous section](#usage) and:
```
python box-plotter.py
```

### Using the traffic generator scripts

Please, refer to [the traffic-gen README file](./traffic-gen/README.md)

## Citing this work

TBD

## License

The original code from upstream did not explicitly specify any license terms. However, the [work contained in this repository](https://github.com/net-ty/mnc_NWDAF/compare/mnc_Public-5G...netlabufjf:nwdaf_ml:ml) is licensed under the GPLv3, as indicated in the [LICENSE](./LICENSE) file, which is reflected in the notice provided below:

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For the json2csv [submodule license](https://github.com/oliveiraleo/PCAP-dataExtractor/blob/main/LICENSE), check [its own notice](https://github.com/oliveiraleo/PCAP-dataExtractor#license).
