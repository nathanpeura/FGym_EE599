
Directory to create folders of different kernels

Currently vadd_DDR is set up with a fake kernel (with correct IO) to be used with testing, the inputs all use DDR

Input 1 uses DDR[0]
Input 2 uses DDR[1] 
Output uses DDR[2]


A makefile is within the folder to create the kernel for the device. If needed, the command to create the kernel is:

```
make all DEVICE=xilinx_u200_xdma_201830_2
```

Subsitute a different device if wish to create the kernel for a different target.

Note that if a kernel and cfg file with a different name than 'vadd' is created then you have to go into the Makefile and change those names. Currently I did not make that flexible since I focused on the Gym folder but can add this flexibility later if wanted. 

