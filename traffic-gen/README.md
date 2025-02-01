# traffic-gen

A folder that contains scripts that implement simple yet customizable network traffic generators.

## Requirements

The requirements from the root README file of the repository cover only the necessary to run the ML pipeline. Besides those, this file requirements cover the necessary to create/reproduce the traffic generated to create the dataset shared on this repository.

### Software

- OS: Ubuntu Server 20.04.6 LTS
- free5gc: [v3.4.4](https://github.com/free5gc/free5gc/releases/tag/v3.4.4)
- UERANSIM: nightly-[01e3785](https://github.com/aligungr/UERANSIM/tree/01e3785420ff7db34fa8723ff34189b8372cf02e)
- go: 1.21.8
- tcpdump: 4.9.3

### Hardware (minimum)

- 2x i5 CPU core (4x on UERANSIM's VM will reduce build times)
- 2GB RAM (4GB is recommended for playing the videos)
- 20GB HDD (for each VM/OS)
- Extra HDD space to record the PCAP files (on free5GC's VM)

**NOTE:** The number of CPUs and amount of RAM will impact directly the time required to build the software.

## Prerequisites

The instructions below do not cover the installation and setup of free5GC and UERANSIM. In broad terms, the environment is required to contain a working [free5GC instance](https://free5gc.org/guide/3-install-free5gc/), with the UERANSIM's device [added to it's database](https://free5gc.org/guide/5-install-ueransim/) and an instance of UERANSIM [configured to connect to free5GC](https://free5gc.org/guide/5-install-ueransim/#6-setting-ueransim).

The URLs linked above may help setting this up. The [free5GC auto deploy](https://github.com/oliveiraleo/free5gc-auto-deploy) tool might be useful too.

## Setup

1. Obtain a copy of the scripts contained on this folder:
```
# UDP server and client
curl -LO https://raw.githubusercontent.com/netlabufjf/nwdaf_ml/refs/heads/ml/traffic-gen/udp-server.sh
curl -LO https://raw.githubusercontent.com/netlabufjf/nwdaf_ml/refs/heads/ml/traffic-gen/udp-client.sh
# Video player script
curl -LO https://raw.githubusercontent.com/netlabufjf/nwdaf_ml/refs/heads/ml/traffic-gen/play-video.sh
```

2. Move `udp-client.sh` and `play-video.sh` inside the `build` folder
```
~/UERANSIM/build
```

**NOTE:** The scripts must be inside of this specific folder in order to be able to run because they require the `nr-binder` utility to work correctly.

Example:
```
# Considering UERANSIM and the scripts are on the home folder, run
mv ~/udp-client.sh ~/UERANSIM/build/
mv ~/play-video.sh ~/UERANSIM/build/
```

3. Move the udp-server.sh script to target/free5GC's machine or run its download command on that machine

Example:
```
# To copy the file using SCP
scp ~/udp-server.sh USER@IP:/home/USER/
```

**TIP:** Change USER and IP according to your setup.

**NOTE:** For SCP to work, SSH must be running and accessible on the target machine.

Or it's possible to run:
```
curl -LO https://raw.githubusercontent.com/netlabufjf/nwdaf_ml/refs/heads/ml/traffic-gen/udp-server.sh
```
On the target machine.

4. Install `tcpdump` on the 5GC machine
```
sudo apt install tcpdump
```

5. If not already done, run the `play-video.sh` script to install the browsers on UERANSIM's machine:
```
bash play-video.sh -prepare
```

## Usage

After running the steps above, to create traffic, follow the steps below

### Generating UDP traffic

On free5GC's machine:

1. Execute free5GC's `run.sh` script to start the 5GC
```
cd ~/free5gc/
./run.sh
```

2. While running the 5GC, start a capture on the upfgtp network interface:
```
sudo tcpdump -v -i upfgtp -w mmtc.pcap
```

3. Run UDP server

**TIP:** `-v` displays the number of captured packets.

On UERANSIM's machine:

1. TODO

### Generating YouTube video traffic

1. TODO

### Generating Naver TV live stream traffic

1. TODO

## Troubleshooting

If the message below appears:
```
[4198:4198:0201/211850.700810:ERROR:ozone_platform_x11.cc(245)] Missing X server or $DISPLAY
[4198:4198:0201/211850.700828:ERROR:env.cc(257)] The platform failed to initialize.  Exiting.
```

Disconnect from UERANSIM's machine SSH session then reconnect again using:
```
ssh USER@IP -X
```

**TIP:** Change USER and IP according to your setup.
