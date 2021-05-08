
/*****
 * Written off of the PLRAM host.cpp example
This example demonstrates how PLRAM feature of the Vitis memory subsystem and
how they
integrate with the Vitis design process.
PLRAMs are small shared memories which are built using the on-chip memory
resources
of the FPGA fabric. They are intended to provide a small amount of data storage
that
application kernels can share and access rapidly. PLRAMs behave just like the
DDR
memory resources managed by the Vitis memory subsystem.
*****/

// OpenCL utility layer include
#include "xcl2.hpp"
#include <algorithm>
#include <stdlib.h>
#include <vector>
#include "headr.h"
// Array Size to access

// Binary File string
std::string binaryFile;

// CPU implementation of Matrix Multiplication
// The inputs are of the size (DATA_SIZE x DATA_SIZE)
void vadd_cpu(int* in1, // Input 1,
               int* in2, // Input 2,
               int* out, // Output addition
               int size //in2 - in1
               ) {
    // Performs vector add = In1 + In2
    for (int i = 0; i < size; i++) {
        out[i] = in1[i]+in2[i];
    }
}

// Functionality to setup OpenCL context and trigger the Kernel
void vadd_fpga(std::vector<int, aligned_allocator<int> >& source_in1,          // Input Matrix 1
                std::vector<int, aligned_allocator<int> >& source_in2,          // Input Matrix 2
                std::vector<int, aligned_allocator<int> >& source_fpga_results, // Output Matrix
                int dim                                                            // One dimension of matrix
                ) {
    int size = dim;
    size_t size_bytes = sizeof(int) * size;

    ////////////////////////////////////////////////////
    cl::CommandQueue q;
    cl::Context context;
    cl::Kernel kernel;
    cl_int err;
    // The get_xil_devices will return vector of Xilinx Devices
    auto devices = xcl::get_xil_devices();
    // read_binary_file() is a utility API which will load the binaryFile
    // and will return the pointer to file buffer.
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    bool valid_device = false;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, NULL, NULL, NULL, &err));
        OCL_CHECK(err, q = cl::CommandQueue(context, device, CL_QUEUE_PROFILING_ENABLE, &err));

        std::cout << "Trying to program device[" << i << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        cl::Program program(context, {device}, bins, NULL, &err);
        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";
            OCL_CHECK(err, kernel = cl::Kernel(program, "vadd", &err));
            valid_device = true;
            break; // we break because we found a valid device
        }
    }
    if (!valid_device) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    ////////////////////////////////////////////////////


    cl::Buffer buffer_in1(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, size_bytes, source_in1.data(), &err);

    cl::Buffer buffer_in2(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, size_bytes, source_in2.data());

    cl::Buffer buffer_output(context, CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY, size_bytes,
                             source_fpga_results.data(), &err);

    /*
     * Using setArg(), i.e. setting kernel arguments, explicitly before
     * enqueueMigrateMemObjects(),
     * i.e. copying host memory to device memory,  allowing runtime to associate
     * buffer with correct
     * DDR banks automatically.
    */

    // int a_row = DATA_SIZE;
    // int a_col = DATA_SIZE;
    // int b_col = DATA_SIZE;

    // Set the kernel arguments
    int narg = 0;
    kernel.setArg(narg++, buffer_in1);
    kernel.setArg(narg++, buffer_in2);
    kernel.setArg(narg++, buffer_output);
    kernel.setArg(narg++, size);


    q.enqueueMigrateMemObjects({buffer_in1, buffer_in2}, 0 /* 0 means from host*/);

    // Launch the kernel
    q.enqueueTask(kernel);

    q.enqueueMigrateMemObjects({buffer_output}, CL_MIGRATE_MEM_OBJECT_HOST);
    q.finish();
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File>" << std::endl;
        return EXIT_FAILURE;
    }

    binaryFile = argv[1];

    // Allocate Memory in Host Memory
    int size = DATA_SIZE;
    size_t size_bytes = sizeof(int) * size;

    std::vector<int, aligned_allocator<int> > source_in1(size_bytes);
    std::vector<int, aligned_allocator<int> > source_in2(size_bytes);
    std::vector<int, aligned_allocator<int> > source_fpga_results(size_bytes);
    std::vector<int, aligned_allocator<int> > source_cpu_results(size_bytes);

    ////////////////////////////////////////////////////
    // Create the test data

    //std::generate(source_in1.begin(), source_in1.end(), std::rand);
    //std::generate(source_in2.begin(), source_in2.end(), std::rand);
    for (int i = 0; i < DATA_SIZE; i++) {
	source_in1[i] = i;
	source_in2[i] = i;
        source_cpu_results[i] = 0; //init to 0 and then call the ftn after
        source_fpga_results[i] = 0;
    }

    // int in1 = 0;

    ////////////////////////////////////////////////////
    //call functions
    printf("Made it here\n");

    // Compute CPU Results
    vadd_cpu(source_in1.data(), source_in2.data(), source_cpu_results.data(), size);
    // mmult_cpu(source_in1.data(), source_in2.data(), source_cpu_results.data(), size);

    // Compute FPGA Results
    vadd_fpga(source_in1, source_in2, source_fpga_results, size);
    // mmult_fpga(source_in1, source_in2, source_fpga_results, size);

    ////////////////////////////////////////////////////
    // Compare the results of FPGA to CPU

    bool match = true;
    for (int i = 0; i < size; i++) {
    	printf("I val: %d, FPGA: %d, Host: %d\n", i,source_fpga_results[i], source_cpu_results[i]);
	 if (source_fpga_results[i] != source_cpu_results[i]) {
            std::cout << "Error: Result mismatch" << std::endl;
            std::cout << "i = " << i << " CPU result = " << source_cpu_results[i]
                      << " FPGA result = " << source_fpga_results[i] << std::endl;
            match = false;
            break;
        }
    }

    std::cout << "TEST " << (match ? "PASSED" : "FAILED") << std::endl;

    return (match ? EXIT_SUCCESS : EXIT_FAILURE);
}
