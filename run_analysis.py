
import os 

def generate_headr(size,bits):

    f = open("src/headr.h", "w")

    data_size = 100800*size
    buff_size = int(data_size/4)
    bit_size = data_size*bits

    str_data = "\n#define DATA_SIZE " + str(data_size) + "\n#define BUFFER_SIZE " + str(buff_size) + "\n"
    print(str_data)
    f.write(str_data)

    f.close()

# os.system('source /opt/xilinx/xrt/setup.sh')

test_lists = [1,4,16,64,256]

#cartpole: 1,16,256,4096
#pong: 1,4,16,64,256

first_loop = True

env = 'pong'

for x in range(len(test_lists)):
    print("#########################################################################################################")
    print("Generating batch size ", test_lists[x])
    generate_headr(test_lists[x], 64)
    os.system('make all DEVICE=xilinx_u200_xdma_201830_2')
    # if(first_loop):
    #     os.system('mkdir xclbin_files')
    #     first_loop = False
    mv_str = 'mv build_dir.hw.xilinx_u200_xdma_201830_2/vadd.xclbin xclbin_files/vadd_DDR_' + env + '_' + str(test_lists[x]) + '.xclbin'
    os.system(mv_str)
    os.system('make cleanall')


#pong:
# void vadd(const uint8_t* in1, // Read-Only Vector 1
#           float* reward,
#           uint8_t* out,     // Output Result
#           int size,                 // Size in integer
#           int batch_size
#           )