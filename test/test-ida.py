import os
import time
import tracemalloc
import sys
import hashlib
import sys


from drex.utils.reliability import ida

def generate_random_bytes(n):
    return os.urandom(n)

#Data in MB
size = int(sys.argv[1])

data = generate_random_bytes(size * 1024 * 1024)
#variable = 4
#data = variable.to_bytes(2, 'big') 

#print(data)
n = int(sys.argv[2])
m = int(sys.argv[3])

#print(data)
start = time.time_ns()/1e+6

disp_result = ida.split_bytes(data, n, m)

end = time.time_ns()/1e+6

print(n,m,end - start)
