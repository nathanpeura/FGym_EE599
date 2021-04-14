
import time
import os
import numpy as np
import pyopencl as cl
os.environ["PYOPENCL_CTX"] = '1'

import gym
env = gym.make('CartPole-v0')
observation = env.reset()

#############################################
size_array = 16
iterations = 100

#############################################

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags

dev =cl.get_platforms()[1].get_devices()
binary = open("xclbin_folder/vadd_16_8.xclbin", "rb").read()

prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed, testing...")

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, size_array*8)
krnl_vadd = cl.Kernel(prg, "vadd")

#############################################
test_pf = True
action = 1
begin_time = time.time()
count = 0
avg_exe_time = 0

for _ in range(iterations): #how many iterations to complete, will likely finish when 'done' is true from env.step
    #####################################
    
    start_time = time.time()
    # create observation and reward from Gym
    observation, reward, done, info = env.step(action)

    gym_time = time.time()
    ###########################
    # populate temporary vectors with numbers, these wont be here when developer fills vectors with real data, so this time will be subtracted  
    tmp = np.full((1,size_array-4),0)
    tmp = tmp.astype(np.float64)
    observation = np.concatenate((observation,tmp), axis=None)
    observation = observation.astype(np.float64)
    a_np = np.float64([observation[0]])
    for x in range(0,size_array-1):
        a_np = np.concatenate((a_np,np.float64(x+observation[0])), axis=None)
    #####################################
    throwaway_time = time.time()
    #call kernel

    a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=observation)
    b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)

    krnl_vadd(queue, (1,), (1,), a_g, b_g, res_g, np.int32(size_array))
    res_np = np.empty_like(a_np)
    cl.enqueue_copy(queue, res_np, res_g)

    vitis_time = time.time()

    action = int(res_np[0]) #assign action to the first value of the result vector

    #####################################

    gym_time -= start_time
    vitis_time -= throwaway_time
    avg_exe_time += gym_time + vitis_time

    print("Gym time: ", gym_time)
    print("Vitis time: ", vitis_time)
    print("Total time: ", gym_time + vitis_time)
    print("-------")

    bool_vec = res_np == (observation+a_np)

    if(not bool_vec.any()):
        test_pf = False
        print("A: ", observation)
        print("B: ", a_np)
        print("Res:      ", res_np)
        print("Expected: ", observation+a_np)
        break

    if done:
       print("Episode finished after {} timesteps".format(count+1))
       break
    
    count += 1

print("Avg Exe time: ", avg_exe_time/iterations)
print("Overall time: ", time.time() - begin_time)

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()