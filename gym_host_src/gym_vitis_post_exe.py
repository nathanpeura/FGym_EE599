
import csv
import numpy as np

def get_vitis_summary():

    exe_count = False

    avg_kernel_exe = []
    f = open("profile_summary.csv", "r")
    # for line in f:
    reader = csv.reader(f, delimiter=",", quotechar='"')
    data_read = [row for row in reader]
    for data in data_read:
        if "Kernel" in data and "Number Of Enqueues" in data: #this finds the "Kernel execution" row and the next row will be the data
            # print(data)
            exe_count = True
        elif exe_count:
            # print(data)
            avg_kernel_exe = data
            exe_count = False

    avg_kernel = np.float64(avg_kernel_exe[4])/1000 #divide by 1000 because it's in ms
    return avg_kernel

print("Kernel avg time (s): ", get_vitis_summary())