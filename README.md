# EE599 Final Project - FGym

Student: Nathan Peura

## FGym

This is the final project for EE599, this project provides an open source ready-to-use platform to test and compare FPGA RL algorithms. The toolkit is implemented to automatically generate the CPU-FPGA interface and provide a RL environment through the OpenAI Gym python library. 

Each folder has its own README files that will explain how to run the code.

### gym_host_src

This folder contains the host files to use to test the benchmark with XCLBIN files. A readme is inside to show how to run the program.

### vitis_accel_src

This folder contains the necessary folder to create a xclbin kernel in Vitis. A readme is inside to show how to make a kernel.

### Bitstream file (.xclbin)

An example XCLBIN file can be downloaded at:

This example file uses:

The current host program is configured to run this XCLBIN file. The params can be seen below.
CartPole-v1 environment
4 parallel environments

## Dependencies

Essential Python packages:

numpy, pyopencl, time, os, sys

Vitis, XRT, and necessary FPGA device drivers are also needed