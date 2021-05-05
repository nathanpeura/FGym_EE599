
import os
import numpy as np
import pyopencl as cl
import time
os.environ["PYOPENCL_CTX"] = '1'
from stable_baselines3.common.env_util import make_vec_env 


import gym


#############################################
episodes = 1
size_observation = 4
parallel_env = 256
size_array = size_observation*parallel_env
environment = 'CartPole-v1'
#############################################

env = make_vec_env(environment, n_envs=parallel_env)
# env = gym.make('Pong-v4')
observation = env.reset()

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags

dev =cl.get_platforms()[1].get_devices()
binary = open("xclbin_folder/analysis_files/cartpole/vadd_DDR_cartpole_"+str(parallel_env)+".xclbin", "rb").read()

prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed, testing...")

# output = np.full((parallel_env), np.uint8(1))
output = np.full((parallel_env), np.float64(1))

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)
krnl_vadd = cl.Kernel(prg, "vadd")

#############################################
test_pf = True
action = np.full((parallel_env), 1)
total_gym_time = 0
total_vitis_time = 0

for x in range(episodes):
    count = 0
    observation = env.reset()
    doneVec = np.full((parallel_env), False)
    for _ in range(10000): #how many iterations to complete, will likely finish when 'done' is true from env.step

        #####################################
        # create observation and reward from Gym

        start_time = time.time()
        # action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        observation = observation.flatten()
        gym_time = time.time()

        observation[0] = np.random.randint(0,6) #first val is used as the action, just random number 0 to 5
        
        # print(type(reward[0]))
        #####################################
        #call kernel

        # for i in range(parallel_env):
        #     if done[i] or doneVec[i]:
        #         if not doneVec[i]:
        #             print("Episode: ",x+1," Env ", i, " finished after {} timesteps".format(count))
        #         doneVec[i] = True
        
        # if(doneVec.all()):
        #     break
        throwaway_time = time.time()

        a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=observation)
        krnl_vadd(queue, (1,), (1,), a_g, res_g, np.float64(reward[0]), np.int32(size_array),np.int32(parallel_env)) #np.int32(reward[0]), np.int32(size_array),np.int32(parallel_env))
        res_np = np.empty_like(output)
        cl.enqueue_copy(queue, res_np, res_g)

        vitis_time = time.time()

        # print(res_np)
        # action = res_np
        gym_time -= start_time
        vitis_time -= throwaway_time
        total_gym_time += gym_time
        total_vitis_time += vitis_time

        count += 1
        # if(count % 200 == 0):
        #     print(count)
        #####################################
            
        # if done.any():
        #     print("Episode number", x, "finished after {} timesteps".format(count+1))
        #     break

total_time = total_gym_time + total_vitis_time #- 3344.97/1000
# total_vitis_time -= 3344.97/1000

spreadsheet_mode = True

if(spreadsheet_mode):
    print(total_time)
    print(total_gym_time)
    print(total_vitis_time)
else:
    print("total time: ", total_time)

    print("total gym time: ", total_gym_time)
    # print("Percent gym time: ", total_gym_time/total_time)

    print("total vitis time: ", total_vitis_time)
    # print("Percent gym time: ", total_vitis_time/total_time)

# if(test_pf):
#     print("Test passed!")
# else:
#     print("Test failed!")

env.close()
