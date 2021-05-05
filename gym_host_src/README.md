
Change the binary xclbin according to where it is stored on your machine!

These files use PyOpenCL to bind to the FPGA through vitis and send data to the kernel, and the kernel sends data back.

use host_program.py to run the RL benchmarking

-- I will add more to this readme this week

One issue I am running into is opening the run summary for the kernel to show the overhead calculations, it will not produce the summary until the program is over. So, for now I separated it into 2 files and the second file reads the summary to print the kernel avg exe time