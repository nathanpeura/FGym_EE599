
import os, sys
import numpy as np
import pyopencl as cl
import time
os.environ["PYOPENCL_CTX"] = '1'
from stable_baselines3.common.env_util import make_vec_env 


import gym

type_observation = ""

################## User input ###########################
episode_num = 1
iteration_max = 1000
parallel_env = 1
environment = 'CartPole-v1'
xclbin_kernel = "vadd_DDR_cartpole_"+str(parallel_env)+".xclbin"
# xclbin_kernel = "xclbin_folder/analysis_files/cartpole_float/vadd_DDR_cartpole_"+str(parallel_env)+".xclbin"
# environment = 'Pong-v4'
# xclbin_kernel = "xclbin_folder/analysis_files/pong_float_reward/vadd_DDR_pong_"+str(parallel_env)+".xclbin"
generate_report = True

block_size = 4
size = 8
#########################################################

blockVec = np.full(block_size,1)
blockMat = np.full((block_size, block_size))
# np.full((1, size_array), 1)

class RL_data:
    def __init__(self):
        self.observation = []
        self.reward = []
        self.action = []
        self.doneVec = []

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

    krnl_vadd = cl.Kernel(prg, "vadd")

    return [ctx,queue,mf,krnl_vadd]

def generate_pre_exe_report(observation_flat,parallel_env,env):
    print("\n########################")
    print("Pre-execution report\n")
    print("----------------------------")
    print("Number of parallel environments: ", parallel_env)
    print("Observation vector elements: ", len(observation_flat))
    print("Observation vector bytes: ", observation_flat.nbytes)
    
    action = np.full((parallel_env), 1) #dummy action vector
    action_output = env.action_space.sample()
    observation, reward, done, info = env.step(action)
    reward_flat = reward.flatten()

    print("----------------------------")
    print("Environment Space")
    print("Observation space: ", env.observation_space)
    print("Action space: ", env.action_space)

    print("----------------------------")
    print("Environment State and Observation Shape")
    print("Observation shape: ", observation.shape)
    print("Reward shape: ", reward.shape)

    print("----------------------------")
    print("Environment IO Data sizes")
    print("Observation element type: ", type(observation_flat[0]))
    print("Reward element type: ", type(reward_flat[0]))
    print("Action element type: ", type(action_output))
    print("----------------------------")





# env = make_vec_env(environment, n_envs=parallel_env)
# observation = env.reset()
# observation_flat = observation.flatten()

# size_array = len(observation_flat)*parallel_env

start_time = time.time()

[ctx,queue,mf,krnl_vadd] = setup_device()

setup_time = time.time()


if(generate_report):
    generate_pre_exe_report(observation_flat, parallel_env,env)

###### create output buffer, change this if your output is different than the type of observation 
    # output = np.full((parallel_env), np.uint8(1))
output = np.full((parallel_env), 1).astype(observation_flat[0]) #(np.float32)

throwaway_time1 = time.time()

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)

setup_time = setup_time - start_time + (time.time() - throwaway_time1) #time it takes to create the buffers and the connection

#############################################
test_pf = True
action = np.full((parallel_env), 1)
total_gym_time = 0
total_vitis_time = 0
total_openCL_time = 0

test_data = RL_data()

for x in range(episode_num):
    print("########## Episode number: ", episode_num, " ##########")
    test_data.observation = env.reset()
    test_data.doneVec = np.full((parallel_env), False)
    for count in range(iteration_max): #how many iterations to complete, will likely finish when 'done' is true from env.step

        #####################################
        # create observation and reward from Gym

        start_time_gym = time.time()
        # action = env.action_space.sample()
        test_data.observation, test_data.reward, done, info = env.step(action)
        observation = test_data.observation.flatten()
        gym_time = time.time()


        observation[0] = np.random.randint(0,6) #first val is used as the action, just random number 0 to 5
        
        # print("iteration: ", count)
        test_data.reward[0] = (np.random.randint(0,6))
        test_data.reward = abs(test_data.reward.astype(np.float32)) #observation_flat[0])

        if(count % 500 == 0):
            print(count)

        # print("Reward: ", test_data.reward)
        #####################################
        #call kernel

        for i in range(parallel_env):
            if done[i] or test_data.doneVec[i]:
                if not test_data.doneVec[i]:
                    print("Episode: ",x+1," Env ", i, " finished after {} timesteps".format(count))
                test_data.doneVec[i] = True
        
        if(test_data.doneVec.all()):
            break


        throwaway_time = time.time()

        obs_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=observation)
        reward_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=test_data.reward)

        openCL_time = time.time()

        krnl_vadd(queue, (1,), (1,), obs_buf, reward_buf, res_g, np.int32(size_array),np.int32(parallel_env)) #np.int32(reward[0]), np.int32(size_array),np.int32(parallel_env))
        
        kernel_time = time.time() 
        
        res_np = np.empty_like(output)
        cl.enqueue_copy(queue, res_np, res_g)

        openCL_time_2 = openCL_time - throwaway_time + time.time() - kernel_time

        test_data.action = res_np

        vitis_time = kernel_time - openCL_time

        # print("Output: ", res_np)

        # print(res_np)
        # action = res_np
        gym_time -= start_time_gym
        total_gym_time += gym_time
        total_vitis_time += vitis_time
        total_openCL_time += openCL_time_2
        kernel_time = kernel_time - openCL_time

        # if(res_np != test_data.reward):
            
        for j in range(len(res_np)):
            if(res_np[j] != test_data.reward[j]):
                print("Not equal!")
                test_pf = False
                break

print("########## Test completed ##########")

total_time = total_gym_time + total_vitis_time + setup_time + total_openCL_time

spreadsheet_mode = False

if(generate_report or spreadsheet_mode):
    if(spreadsheet_mode):
        print(total_time)
        print(setup_time)
        print(total_openCL_time)
        print(total_gym_time)
        print(total_vitis_time)
    else:
        # print("Post-execution report: ")
        # print("total time: ", total_time)
        # print("setup time: ", setup_time)
        # print("Opencl time: ", total_openCL_time)
        f = open("data_out.txt", "w")
        str_data = str(total_time-total_gym_time-total_vitis_time) + "\n" + str(total_time) + "\n"
        f.write(str_data)
        f.close()

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()
