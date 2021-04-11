


This is adapted from the vitis accel git repo. 

To create a kernel, run:

make all DEVICE=xilinx_u200_xdma_201830_2







------ From the vitis accel examples git -----------------


PLRAM Memory Access (C)
=======================

This example shows the usage of PLRAM and how to use it with simple matrix multiplication (Row x Col).

**KEY CONCEPTS:** Vitis Memory Hierarchy, PLRAMs

**KEYWORDS:** PLRAM

EXCLUDED PLATFORMS
------------------

Platforms containing following strings in their names are not supported for this example :

::

   _u25_
   u30
   zc
   vck
   u50
   samsung
   _u2_
   nodma

DESIGN FILES
------------

Application code is located in the src directory. Accelerator binary files will be compiled to the xclbin directory. The xclbin directory is required by the Makefile and its contents will be filled during compilation. A listing of all the files in this example is shown below

::

   src/host.cpp
   src/mmult.cpp
   
COMMAND LINE ARGUMENTS
----------------------

Once the environment has been configured, the application can be executed by

::

   ./plram_access <mmult XCLBIN>

DETAILS
-------

This example demonstrates how ``PLRAM`` feature of the Vitis memory
subsystem and how they integrate with the Vitis design process.

PLRAM is small shared memory which is built using the on-chip memory
resources of the FPGA fabric. It is intended to provide a small amount
of data storage that application kernels can share and access
rapidly(lowest latency). PLRAM behaves just like the DDR memory
resources managed by the Vitis memory subsystem.

PLRAM can be assigned to a buffer by using ``--sp`` tags in the kernel
linking stage.

::

   --sp mmult_1.a:PLRAM[0] --sp mmult_1.b:DDR[0] --sp mmult_1.c:PLRAM[1]

For more comprehensive documentation, `click here <http://xilinx.github.io/Vitis_Accel_Examples>`__.
