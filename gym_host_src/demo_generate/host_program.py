
import os, sys
import numpy as np
import pyopencl as cl
import time
os.environ["PYOPENCL_CTX"] = '1'

################## User input ###########################
iteration_max = 1
xclbin_kernel = "top.xclbin"
generate_report = True

##########

data_size = 16
out_size = 4
#-------------
block_size = 4
size = 8
#########################################################

blockVec = np.full(block_size,1).astype(np.float32)
blockMat = np.full((block_size, block_size),0).astype(np.float32)

def setup_device():
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags

    dev =cl.get_platforms()[1].get_devices()
    binary = open(xclbin_kernel, "rb").read()

    prg = cl.Program(ctx,dev,[binary])
    prg.build()
    print(dev)
    print("Device is programmed, testing...")

    krnl_vadd = cl.Kernel(prg, "top")

    return [ctx,queue,mf,krnl_vadd]


A_vec = np.array(data_size*[blockVec])
B_vec = A_vec

C_mat = np.array(out_size*[blockMat])

[ctx,queue,mf,krnl_vadd] = setup_device()

print("Vec A: ", A_vec)
print("Vec B: ", B_vec)

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, C_mat.nbytes)

for count in range(iteration_max):

    a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=A_vec) #mf.COPY_HOST_PTR prevents the xrt warning but figured I used use host ptr since that is what the host.cpp uses
    b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=B_vec)

    krnl_vadd(queue, (1,), (1,), a_buf, b_buf, res_g)
    
    res_np = np.empty_like(C_mat)
    cl.enqueue_copy(queue, res_np, res_g)

    print("Output:\n", res_np)


print("########## Test completed ##########")

