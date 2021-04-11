
Directory to create folders of different kernels

Currently I am testing with vadd_PLRAM, which has 2 vector inputs, one vector output. 

This kernel adds the two vectors and sends it on the output. 

Input 1 uses PLRAM[0]

Input 2 uses DDR[0] <- I will change this to PLRAM since access latency is lowest, but need to run some tests

Output uses PLRAM[1]



