# NWDAF ML

This repository presents a proof-of-concept (PoC) demonstrating the application of Machine Learning (ML) functionality based on the specifications of the Network Data Analytics Function (NWDAF) implementation for the classification of 5G devices solely based on their observed traffic.

## Tested Environment Configuration

### Software

- python: 3.13.1
- pip: 25.0.1
- python packages from [requirements.txt](./requirements.txt)
- tshark: 4.4.3
- perl: 5.40.1

### Hardware

The hardware specifications below concern the ML experiment pipeline (e.g. processing the dataset, training models and running inference). For the hardware and software requirements for generating a new 5G simulated traffic dataset, please, refer to [the traffic-gen README file](./traffic-gen/README.md).

#### Minimum

- 4x 3.0GHz CPU cores
- 16GB of RAM
- `A`GB HDD to store the input dataset
- ~11.3x`A` HDD available to store the temporary files of preprocessed data
- ~2x`A` HDD to store the preprocessed data

**TIP:** The dataset used to obtain these specifications was a subset of the [full dataset](./README.md#dataset-description) and had 19.6GB training + 2.4GB inference data (i.e. `A = 22GB`), see the values on the list [below](./README.md#recommended) for a concrete example.

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

## Quick comparison between [Kim et al. 2022], our previous work and current work

The authors of [[Kim et al. 2022]](https://doi.org/10.1109/ICCE53296.2022.9730290) implemented the NWDAF module and its submodules (MTLF and AnLF) integrated to free5GC, however, they used an image dataset as their ML functionality.

Previously, a reprodction of [Kim et al. 2022]'s work was made on [[de Oliveira et al. 2024]](https://doi.org/10.1109/ISCC61673.2024.10733717) ([that README](https://github.com/oliveiraleo/mnc_NWDAF/blob/mnc_Public-5G/README.md) details the environment used in this process). After that, [another ML functionality](https://github.com/oliveiraleo/mnc_NWDAF/tree/mnc_Public-5G/ML_test_code) closely related to Computer Networks field was implemented. Instead of using an image dataset, a [packet capture dataset](https://github.com/oliveiraleo/mnc_NWDAF/tree/mnc_Public-5G/ML_test_code/dataset) containing 6 captures of 1000 packets each was created. This dataset was used to test the new ML functionality and the instructions to reproduce the environment used for this second phase are located on [that other file](https://github.com/oliveiraleo/mnc_NWDAF/blob/mnc_Public-5G/VMs-setup.md). The integration between [Kim et al. 2022]'s NWDAF and [de Oliveira et al. 2024]'s ML functionality wasn't finished.

Our current work focused on two main points: (i) creating a larger 5G simulated public PCAP dataset; and (ii) enhancing the classification results obtained on [de Oliveira et al. 2024].

The dataset was created with 1 million packets for each capture. Builing upon the implementation done by [de Oliveira et al. 2024], the current work reimplemented the complete machine learning pipeline to include 8 models and 33 features (previously there was only 3 models and 7 features) extracted from the PCAP files. The data used for training and testing the models didn't overlap with the data used for inference (more details in the [section below](./README.md#dataset-description)).

TODO: detail our results

## Dataset description

The used dataset was divided in two parts: training data and inference data.

In general, classification ML models require a large amount of data to work well. Our previous work contained only 3000 packets for training the models and another 3000 to run inferences. To improve that, we focused on having around 10 million packets for each class on the training phase. 

Considering an application of our work (5G user equipment traffic classification), we expect that real world systems that work the same way our implementation was design would have some data to be trained on then would have the models used for inference in another dataset. For example: a mobile network operator might train a classification model in a test environment, then deploy this model in a production environment and use its output to have some insight or make a decision. Because of that, it was decided that the training and inference datasets would not overlap.

With those objectives in mind, it was possible to find two public 5G datasets ("[5G Traffic Datasets](https://dx.doi.org/10.21227/ewhk-n061)" and "[5G Campus Networks: Measurement Traces](https://dx.doi.org/10.21227/xe3c-e968)") that contained data that we could use to train models. For the inference set, the description of the steps taken to create the datasets we've used in training were taken into account and, as close as possible, implemented on our 5G simulated testing environment.

### Training set

- file_name.pcap: disk_size; number_of_packets; class**; comments
- `Youtube_cellular.pcap`: 12.4GB; 10,774,692; eMBB; obtained from "5G Traffic Datasets"
- `naver5g3-10M.pcap`: 11.8GB; 10,248,958; URLLC; a 10M packet cut from the file naver5g3.pcap obtained from "5G Traffic Datasets"
- `*.100.pcap` (10 files in total): 169.6MB; 1,000,000***; mMTC; obtained from "5G Campus Networks: Measurement Traces"

### Inference set

- file_name.pcap: disk_size; number_of_packets; class**; comments
- `youtube-1M-1080p.pcap`: 1.3GB; 1,004,464; eMBB; captured during the playback of [this playlist](https://www.youtube.com/watch?v=LXb3EKWsInQ&list=PLrN5hDSKBQCLN_p4SJwqHSNO3ToomP-il&index=1)
- `naver-tv-1M.pcap`: 1.1GB; 1,042,918; URLLC; captured during the video live streaming of [this channel](https://tv.naver.com/ytnnews24)
- `udp-100pps.pcap`: 97.4MB; 1,069,973; mMTC; captured using the UDP client with 100 packets/sec (as described on [[Rischke et al. 2021]](https://doi.org/10.1109/ACCESS.2021.3108423), the same authors of the "[5G Campus Networks: Measurement Traces](https://dx.doi.org/10.21227/xe3c-e968)" dataset)
- `udp-nc-traffic-1k.pcap`: 88kB; 1,007; mMTC; captured using the UDP client with the probabilistic approach described on [[Sivanathan et al. 2017]](https://doi.org/10.1109/INFCOMW.2017.8116438)

** Classes based on [ITU's M.2083-0 recommendation](https://www.itu.int/rec/R-REC-M.2083-0-201509-I/en)

*** To the best of our knowledge, there isn't any real world PCAP dataset containing 10 million mMTC packets on a single capture, the closest it was possible to find at this time were the captures from "5G Campus Networks: Measurement Traces" dataset that account for 1 million packets in total

**NOTE:** The scripts used to create this data and details of the environment are available on `traffic-gen` [folder](./traffic-gen/).

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

**NOTE:** On its current implementation, the inference script will check for data that still needs to be preprocessed before running inference. This was designed to handle the use case where the inference data is added to the input folder only after running the training pipeline with the training data.

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

## Acknowledgements

I'd like to acknowledge Mr [Rodrigo Oliveira](https://github.com/rsilvoliveira) for all comments and tips he gave during the coding phase of this work. I'd like to also thank the anonymous reviewers and conference participants who provided valuable feedback on our previous work, contributing to the development of this research.

## License

The original code from upstream did not explicitly specify any license terms. However, the [work contained in this repository](https://github.com/net-ty/mnc_NWDAF/compare/mnc_Public-5G...netlabufjf:nwdaf_ml:ml) is licensed under the GPLv3, as indicated in the [LICENSE](./LICENSE) file, which is reflected in the notice provided below:

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For the json2csv [submodule license](https://github.com/oliveiraleo/PCAP-dataExtractor/blob/main/LICENSE), check [its own notice](https://github.com/oliveiraleo/PCAP-dataExtractor#license).
