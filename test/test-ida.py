import os
import time
from drex.utils.reliability import ida

def generate_random_bytes(n):
    return os.urandom(n)

data = generate_random_bytes(10000000)
n = 5
m = 3


start = time.time_ns()/1e+6

fragments = ida.split_bytes(data, n, m)
end = time.time_ns()/1e+6

#print("fragments = ", fragments)
print("Old",end-start)

