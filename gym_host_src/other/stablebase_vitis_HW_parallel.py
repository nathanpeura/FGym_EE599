import gym
import pyopencl as cl
import numpy as np
os.environ["PYOPENCL_CTX"] = '1'
# https://github.com/oysstu/pyopencl-in-action/blob/master/ch7/user_event.py

# from stable_baselines3.common.env_util import make_atari_env
# from stable_baselines3.common.vec_env import VecFrameStack
# from stable_baselines3 import A2C

# env = make_atari_env('PongNoFrameskip-v4', n_envs=4, seed=0)
# # Frame-stacking with 4 frames
# # env = VecFrameStack(env, n_stack=4)
# # env = gym.make('PongNoFrameskip-v4')

# print("action space: ", env.action_space)
# print("Observation space: ", env.observation_space)

# obs = env.reset()
# for i in range(0,5):
#     action = [1,1,1,1] #arbitrary value for each of the 4 env actions
#     # action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     print("Observation shape: ", obs.shape)
#     # env.render()

# print("Finished testing!")

# count = 0
# parallel_env_agent = 1
# size_array = 16

# ctx = cl.create_some_context()
# queue = cl.CommandQueue(ctx,None,cl.command_queue_properties.OUT_OF_ORDER_EXEC_MODE_ENABLE)

# mf = cl.mem_flags

# dev =cl.get_platforms()[1].get_devices()
# binary = open("../xclbin_folder/vadd_flg_16_8.xclbin", "rb").read()
# prg = cl.Program(ctx,dev,[binary])
# prg.build()
# print(dev)
# print("Device is programmed, testing...")

# res_g = cl.Buffer(ctx, mf.WRITE_ONLY, 8*size_array)
# krnl_vadd = cl.Kernel(prg, "vadd")

# #create user event
# user_event = cl.UserEvent(ctx)

# def read_complete(status, data):
#     print('Output: ' + str(data))

# global_size = (1,)
# local_size = (1,)

# vec_1 = np.arange(16, dtype=np.float64)
# # vec_1 = vec_1.astype(np.float64)
# vec_2 = vec_1

# a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=vec_1)
# b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=vec_2)

# # __call__(queue, global_size, local_size, *args, global_offset=None, wait_for=None, g_times_l=False)
# kernel_event = krnl_vadd.user_event(queue, global_size, local_size, res_g, wait_for=[user_event])

# # Enqueue command to copy from buffers to host memory
# read_event = cl.enqueue_copy(queue, dest=vec_1, src=res_g, is_blocking=False, wait_for=[kernel_event])
# read_event = cl.enqueue_copy(queue, dest=vec_2, src=res_g, is_blocking=False, wait_for=[kernel_event])

# read_event.set_callback(cl.command_execution_status.COMPLETE, lambda s: read_complete(s, data=res_g))
