import os
import time
import tracemalloc

# importing libraries
import os
import psutil
 
# inner psutil function
def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss
 
# decorator function
def profile(func):
    def wrapper(*args, **kwargs):
 
        mem_before = process_memory()
        result = func(*args, **kwargs)
        mem_after = process_memory()
        print("{}:consumed memory: {:,}".format(
            func.__name__,
            mem_before, mem_after, mem_after - mem_before))
 
        return result
    return wrapper


from drex.utils.reliability import ida

def generate_random_bytes(n):
    return os.urandom(n)

# instantiation of decorator function
@profile
def execute():

    
    data = generate_random_bytes(300000000)
    #variable = 4
    #data = variable.to_bytes(2, 'big') 
    
    #print(data)
    n = 5
    m = 3

    #store data into a file
    output = open("data.txt", "wb")
    output.write(data)
    output.close()

    start = time.time_ns()/1e+6

    disp_result = ida.split_bytes(data, n, m)
    
    print(len(disp_result))
    
    total = 0
    for d in disp_result:
        total += len(d.content)
        print(len(d.content))
    #print(disp_result)
    
    print(total)
    print(len(data))
    print(len(data) / m * n)

    
    #fragments = ida.split_bytes_v2(data, n, m)
    #res = ida.merge_bytes_v2(fragments, n, m)
    #fragments = ida.split_bytes_v0(data, n, m)
    #result = ida.assemble_bytes(fragments)
    #print(result)
    end = time.time_ns()/1e+6

    #print("fragments = ", fragments)
    print("Old",end-start)
    
execute()