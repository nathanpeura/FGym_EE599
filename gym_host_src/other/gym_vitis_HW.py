
import os
import numpy as np
import pyopencl as cl
import time
os.environ["PYOPENCL_CTX"] = '1'
from stable_baselines3.common.env_util import make_vec_env 


import gym


#############################################
episodes = 3
size_array = 100800

#############################################

# env = make_vec_env('Pong-v4', n_envs=parallel_env)
env = gym.make('Pong-v4')
observation = env.reset()

b_np = np.full((1, size_array), 1)
b_np = b_np.astype(np.float64)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags

dev =cl.get_platforms()[1].get_devices()
binary = open("xclbin_folder/vadd_100800_25200_PLRAM_pong.xclbin", "rb").read()

prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed, testing...")

output = np.full((1), np.uint8(1))

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)
krnl_vadd = cl.Kernel(prg, "vadd")

#############################################
test_pf = True
action = env.action_space.sample()
total_gym_time = 0
total_vitis_time = 0
iterations = 0
# for x in range(episodes):
count = 0
observation = env.reset()
for _ in range(10000): #how many iterations to complete, will likely finish when 'done' is true from env.step

    #####################################
    # create observation and reward from Gym

    # action = env.action_space.sample()
    start_time = time.time()

    observation, reward, done, info = env.step(action)
    observation = observation.flatten()

    gym_time = time.time()

    observation[0] = np.random.randint(0,6) #first val is used as the action, just random number 0 to 5
    
    #####################################
    #call kernel

    # if done:
    #     print("Episode: ",x+1, " finished after {} timesteps".format(count))
    #     break

    throwaway_time = time.time()

    a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=observation)
    krnl_vadd(queue, (1,), (1,), a_g, res_g, np.int32(reward), np.int32(size_array))
    res_np = np.empty_like(output)
    cl.enqueue_copy(queue, res_np, res_g)

    vitis_time = time.time()

    gym_time -= start_time
    vitis_time -= throwaway_time
    total_gym_time += gym_time
    total_vitis_time += vitis_time


    # print(res_np)
    action = res_np[0]

    count += 1
    iterations += 1

total_time = total_gym_time + total_vitis_time - 2395.58/1000
total_vitis_time -= 2395.58/1000


print("total time: ", total_time)
print("Number of iterations: ", iterations)

print("total gym time: ", total_gym_time)
print("Percent gym time: ", total_gym_time/total_time)

print("total vitis time: ", total_vitis_time)
print("Percent gym time: ", total_vitis_time/total_time)

# print("Avg Gym time: ", total_gym_time/iterations)
# print("Avg Vitis time: ", total_vitis_time/iterations)

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()
