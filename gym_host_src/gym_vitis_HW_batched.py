
import os
import numpy as np
import pyopencl as cl
os.environ["PYOPENCL_CTX"] = '1'

import gym
env = gym.make('CartPole-v0')
observation = env.reset()

#############################################
count = 0

size_array = 4096

#a_np = np.random.randint(0,10,size_array)
b_np = np.full((1, size_array), 1)
# np.random.randint(0,10,size_array)
b_np = b_np.astype(np.float64)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
# a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)

dev =cl.get_platforms()[1].get_devices()
binary = open("vadd_flg_4096_4096.xclbin", "rb").read()
prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed, testing...")

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, b_np.nbytes)
krnl_vadd = cl.Kernel(prg, "vadd")

#############################################
test_pf = True
np.set_printoptions(precision=10)

for _ in range(1000): #how many iterations to complete, will likely finish when 'done' is true from env.step
    #####################################
    # create observation and reward from Gym
    action = env.action_space.sample()
    observation, reward, done, info = env.step(action)
    # observation = observation*10 #test to make them greater than 1 
    a_np = np.full((1, size_array), observation[0])
    # b_np = b_np.astype(np.float64)

    num_obs = int(size_array/len(observation))
    tmp = observation

    #create "batched" observations of the same observation
    for x in range(0,num_obs-1):
        observation = np.concatenate((observation,tmp), axis=None)
    
    #####################################
    #call kernel

    a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=observation)
    b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)

    krnl_vadd(queue, (1,), (1,), a_g, b_g, res_g, np.int32(size_array))
    res_np = np.empty_like(b_np)
    cl.enqueue_copy(queue, res_np, res_g)

    #####################################

    # print("A: ", observation)
    # print("B: ", a_np)
    # print("Res:      ", res_np)
    # print("Expected: ", observation+b_np)

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

    count = count + 1

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()
