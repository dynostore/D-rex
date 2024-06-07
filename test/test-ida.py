import os
import time
import tracemalloc
import sys
import hashlib


from drex.utils.reliability import ida

def generate_random_bytes(n):
    return os.urandom(n)

#Data in MB
size = 100

data = generate_random_bytes(size * 1024 * 1024)
#variable = 4
#data = variable.to_bytes(2, 'big') 

#print(data)
n = 5
m = 3

#print(data)
start = time.time_ns()/1e+6

disp_result = ida.split_bytes(data, n, m)

end = time.time_ns()/1e+6

print("Time: ", end - start)
