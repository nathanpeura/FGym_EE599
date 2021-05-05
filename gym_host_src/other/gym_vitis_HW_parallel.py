import gym

from stable_baselines3.common.env_util import make_vec_env 
from stable_baselines3.common.cmd_util import make_atari_env

#############################################

import os
import numpy as np
import pyopencl as cl
os.environ["PYOPENCL_CTX"] = '1'

import gym
env = gym.make('CartPole-v0')
observation = env.reset()

#############################################
count = 0

size_array = 16

b_np = np.full((1, size_array), 1)
b_np = b_np.astype(np.float64)

ctx = cl.create_some_context()
queue = [cl.CommandQueue(ctx),cl.CommandQueue(ctx)]

mf = cl.mem_flags

dev =cl.get_platforms()[1].get_devices()
binary = open("../xclbin_folder/vadd_16_8.xclbin", "rb").read()
prg = cl.Program(ctx,dev,[binary])
prg.build()
print(dev)
print("Device is programmed")

res_g = [cl.Buffer(ctx, mf.WRITE_ONLY, b_np.nbytes),cl.Buffer(ctx, mf.WRITE_ONLY, b_np.nbytes)]
krnl_vadd = [cl.Kernel(prg, "vadd"), cl.Kernel(prg, "vadd")]

print("Created ", len(krnl_vadd), " parallel kernels! Testing...")
##################
test_pf = True

env = make_vec_env("CartPole-v1", n_envs=2)

obs = env.reset()
for _ in range(4):
    action = [1,1] #env.action_space.sample()
    # print("action: ", action)
    obs, rewards, dones, info = env.step(action)
    # print("observation: ", obs)
    print("count: ", count)


    for i in range(0,2):
        a_np = np.full((1, size_array), 1)
        num_obs = int(size_array/len(obs[i]))

        tmp = obs[i]
        for x in range(0,num_obs-1):
            tmp = np.concatenate((tmp,obs[i]), axis=None)
        # print("tmp: ", tmp)
        a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tmp)
        b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
        krnl_vadd[i](queue[i], (1,), (1,), a_g, b_g, res_g[i], np.int32(size_array))
        res_np = np.empty_like(b_np)
        cl.enqueue_copy(queue[i], res_np, res_g[i])

        bool_vec = res_np == (tmp+a_np)

        # print("A: ", tmp)
        # print("B: ", a_np)
        # print("Res:      ", res_np)
        # print("Expected: ", tmp+b_np)

        if(not bool_vec.any()):
            print("i: ", i)
            test_pf = False
            print("A: ", tmp)
            print("B: ", a_np)
            print("Res:      ", res_np)
            print("Expected: ", tmp+a_np)
            # break


        #env.render()
        # print("Observation: ", obs)
        if(dones.any()):
            print("Completed!")
            break
    count += 1

if(test_pf):
    print("Test passed!")
else:
    print("Test failed!")

env.close()
