
Change the binary xclbin according to where it is stored on your machine!

These two files use PyOpenCL to bind to the FPGA through vitis and send data to the kernel, and the kernel sends data back.

gym_vitis_HW.py basically sends a single observation vector as input A and random data as input B, then the kernel returns A + B vector add

gym_vitis_HW_batched.py sends input A as repeated observation vector to act as 'batched' data as if someone would like to send larger than a single observation vector, input B is observation[0] to act as data to add with A, the kernel returns A + B

Currently working on a parallel environment and agent python script