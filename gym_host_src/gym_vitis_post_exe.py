
import csv
import numpy as np

def get_vitis_summary(spreadsheet_mode):

    exe_count = False

    data_kernel_exe = []
    data_host_transfer_read = []
    data_host_transfer_write = []
    data_kernel_mem_read = []
    data_kernel_mem_write = []
    f = open("profile_summary.csv", "r")
    # for line in f:
    reader = csv.reader(f, delimiter=",", quotechar='"')
    data_read = [row for row in reader]
    for x in range(len(data_read)):
        if "Kernel Execution" in data_read[x] and not exe_count: #this finds the "Kernel execution" row and the next row will be the data
            data_kernel_exe = data_read[x+2]
            exe_count = True #have to use this because title comes up again later
        if "Data Transfer: Host to Global Memory" in data_read[x]: #this finds the "Kernel execution" row and the next row will be the data
            data_host_transfer_read = data_read[x+2]
            data_host_transfer_write = data_read[x+3]
        if "Data Transfer: Kernels to Global Memory" in data_read[x]: #this finds the "Kernel execution" row and the next row will be the data
            data_kernel_mem_read = data_read[x+2] 
            data_kernel_mem_write = data_read[x+3] 
            
    #kernel execution          
    kernel_total_time = np.float64(data_kernel_exe[2])
    avg_kernel = np.float64(data_kernel_exe[4]) #divide by 1000 because it's in ms

    #data transfer: host to global mem

    host_mem_transferrate_read = np.float64(data_host_transfer_read[3])
    host_mem_util_read = np.float64(data_host_transfer_read[4])
    host_mem_total_time_read = np.float64(data_host_transfer_read[6])

    host_mem_transferrate_write = np.float64(data_host_transfer_write[3])
    host_mem_util_write = np.float64(data_host_transfer_write[4])
    host_mem_total_time_write = np.float64(data_host_transfer_write[6])

    total_transfer_time = host_mem_total_time_read + host_mem_total_time_write
    avg_util = (host_mem_util_read + host_mem_util_write)/2
    avg_transfer_rate = (host_mem_transferrate_read + host_mem_transferrate_write)/2

    #data transfer: kernel to global mem
    kernel_mem_transfer_rate_read = np.float64(data_kernel_mem_read[6])
    kernel_mem_util_read = np.float64(data_kernel_mem_read[7])
    kernel_mem_avg_latency_read = np.float64(data_kernel_mem_read[9])

    kernel_mem_transfer_rate_write = np.float64(data_kernel_mem_write[6])
    kernel_mem_util_write = np.float64(data_kernel_mem_write[7])
    kernel_mem_avg_latency_write = np.float64(data_kernel_mem_write[9])

    if(spreadsheet_mode):
        print(kernel_total_time)
        print(total_transfer_time)
        print(f'{host_mem_util_read:.10f}')
        print(f'{host_mem_util_write:.10f}')
        print(host_mem_transferrate_read)
        print(host_mem_transferrate_write)
        f = open("xclbin_folder/analysis_files/data_out.txt", "a")
        str_data = str(kernel_total_time) + "\n" + str(total_transfer_time) + "\n" + str(f'{host_mem_util_read:.10f}') + "\n" + str(f'{host_mem_util_write:.10f}') + "\n" + str(host_mem_transferrate_read) + "\n" + str(host_mem_transferrate_write) + "\n"
        f.write(str_data)
        f.close()
    else:
        print("Kernel time: ", kernel_total_time, ' ms')
        print("Total transfer time: ", total_transfer_time, ' ms')
        print("Util read: ", host_mem_util_read, "%\nUtil write: ", host_mem_util_write, "%")
        print("transfer rate read: ", host_mem_transferrate_read, " MB/s\ntransfer rate write: ", host_mem_transferrate_write, ' MB/s')

    return avg_kernel

# print("Kernel avg time (s): ", get_vitis_summary())
get_vitis_summary(True)