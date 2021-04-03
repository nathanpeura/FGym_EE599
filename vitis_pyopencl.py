
# import os
# import numpy as np
# import pyopencl as cl
# os.environ["PYOPENCL_CTX"] = '1'

# size_array = 10

# a_np = np.random.randint(0,10,size_array)
# b_np = np.random.randint(0,10,size_array)

# ctx = cl.create_some_context()
# queue = cl.CommandQueue(ctx)

# mf = cl.mem_flags
# a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
# b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)

# dev =cl.get_platforms()[1].get_devices()
# binary = open("vadd_cp.xclbin", "rb").read()
# prg = cl.Program(ctx,dev,[binary])
# prg.build()
# print(dev)

# res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

# krnl_vadd = cl.Kernel(prg, "vadd")
# krnl_vadd(queue, (1,), (1,), a_g, b_g, res_g, np.int32(size_array*2))

# res_np = np.empty_like(a_np)
# cl.enqueue_copy(queue, res_np, res_g)

# print("A: ", a_np)
# print("B: ", b_np)
# print("Res: ", res_np)

import os
import numpy as np
import pyopencl as cl
os.environ["PYOPENCL_CTX"] = '1'

size_array = 8

a_np = np.random.randint(0,10,size_array)
b_np = np.random.randint(0,10,size_array)

a_np = a_np.astype(np.float64)
b_np = b_np.astype(np.float64)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)

dev =cl.get_platforms()[1].get_devices()
binary = open("vadd_double.xclbin", "rb").read()
prg = cl.Program(ctx,dev,[binary])
# prg = cl.Program(ctx, [dev], [open("vadd_cp.xclbin").read()])
prg.build()
print(dev)

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

krnl_vadd = cl.Kernel(prg, "vadd")
#krnl_vadd.set_args(a_g,b_g,res_g,np.int32(size_array))
# ev = cl.enqueue_nd_range_kernel(queue, krnl_vadd, a_np.shape, None)
krnl_vadd(queue, (1,), (1,), a_g, b_g, res_g, np.int32(size_array))

res_np = np.empty_like(a_np)
cl.enqueue_copy(queue, res_np, res_g)

print("A: ", a_np)
print("B: ", b_np)
print("Res: ", res_np)