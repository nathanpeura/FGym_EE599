
# going to add some object oriented logic later to make it cleaner
# Parallel environment and (serial but parallel) agents
# need to find out if it is worth it to fork and join the kernel call so you can call the kernels at the same time rather than a for loop

import os
import numpy as np
import pyopencl as cl
os.environ["PYOPENCL_CTX"] = '1'

import gym
from stable_baselines3.common.env_util import make_vec_env 

#############################################
#set up the device to be programmed by the xclbin
# and create the kernel
parallel_env_agent = 4
size_array = 16384
numEpisodes = 5

# b_np = np.full((1, size_array), 1)
# b_np = b_np.astype(np.float64)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx) #,None,cl.command_queue_properties.OUT_OF_ORDER_EXEC_MODE_ENABLE)

mf = cl.mem_flags
# a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)

dev =cl.get_platforms()[1].get_devices()
binary = open("../xclbin_folder/vadd_16384_4096.xclbin", "rb").read()
prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed, testing...")

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, 8*size_array) #np.float64 = 64 bits / 8 = 8 bytes, size array is how many of them
krnl_vadd = cl.Kernel(prg, "vadd")
# for i in range(0,parallel_env_agent):
#     krnl_vadd.append(cl.Kernel(prg, "vadd"))

#############################################
# env = gym.make('CartPole-v0')
env = make_vec_env("CartPole-v1", n_envs=parallel_env_agent)
observation = env.reset()

test_pf = True
np.set_printoptions(precision=10)

for x in range(numEpisodes):
    print("Episode: ", x+1)
    doneVec = np.full((parallel_env_agent), False)
    count = 0
    while True: #how many iterations to complete, will likely finish when 'done' is true from env.step
        #####################################
        # create observation and reward from Gym
        action = [env.action_space.sample(),env.action_space.sample(),env.action_space.sample(),env.action_space.sample()]
        observation, reward, done, info = env.step(action)

        # print("Reward: ", reward) #think about moving this to input B
        
        count = count + 1

        #####################################
        #call kernel

        for i in range(0,parallel_env_agent):
            if done[i] or doneVec[i]:
                if not doneVec[i]:
                    print("Env: ", i, " Episode finished after {} timesteps".format(count))
                doneVec[i] = True
            else:    
                # print("Observation: ", observation)
                tmp = observation[i]
                tmp_obs = observation[i]
                num_obs = int(size_array/len(observation[i]))
                #####################################
                #create "batched" observations of the same observation
                for x in range(0,num_obs-1):
                    tmp_obs = np.concatenate((tmp_obs,tmp), axis=None)
                tmp_obs = tmp_obs.astype(np.float64) #need this because it will produce an error otherwise
                
                a_np = np.float64([observation[i][0]+i]) #arbitrary numbers for vector 2
                for x in range(0,size_array-1):
                    a_np = np.concatenate((a_np,np.float64(x+x*i+observation[i][0])), axis=None)
                #####################################
                #fill the buffers and call the kernel
                a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tmp_obs)
                b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
                
                krnl_vadd(queue, (1,), (1,), a_g, b_g, res_g, np.int32(size_array))
                res_np = np.empty_like(a_np)
                cl.enqueue_copy(queue, res_np, res_g)

                #####################################

                # print("A: ", tmp_obs)
                # print("B: ", a_np)
                # print("Res:      ", res_np)
                # print("Expected: ", tmp_obs+a_np)

                bool_vec = res_np == (tmp_obs+a_np)

                if(not bool_vec.any()):
                    print("count: ", count)
                    test_pf = False
                    print("A: ", tmp_obs)
                    print("B: ", a_np)
                    print("Res:      ", res_np)
                    print("Expected: ", tmp_obs+a_np)
                    break
        if(doneVec.all()):
            break

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()
