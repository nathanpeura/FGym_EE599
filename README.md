# EE599_gym_vitis

## gym_vitis_HW.py

This is the host code to run within the FPGA, to run:

First, add vitis paths: 

`source /opt/xilinx/xrt/setup.sh`

Next, as long as the .xclbin file is in the directory run with: 

`python gym_vitis_HW.py`

## vitis_pyopencl.py

This file is host code without GYM, used for general debug and initial connection. 

## vadd.cpp 

This is the kernel file, let me know if you need the config files that I used to build the .xclbin
