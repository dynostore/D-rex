import os
import time
import tracemalloc
import sys
import hashlib


from drex.utils.reliability import ida

def generate_random_bytes(n):
    return os.urandom(n)


data = generate_random_bytes(10)
#variable = 4
#data = variable.to_bytes(2, 'big') 

#print(data)
n = 5
m = 3

#print(data)
start = time.time_ns()/1e+6

# store data in a file
with open("original.txt", "wb") as f:
    f.write(data)

disp_result = ida.split_bytes(data, n, m)

#store fragments in a file
for d in range(n):
    with open("fragment"+str(d)+".txt", "wb") as f:
        f.write(disp_result[d].content)

#res2 = ida.split_bytes_v0(data, n, m)
#to_recover = disp_result[0:m]
#print(to_recover)
result = ida.assemble_bytes(disp_result)


#Get hash of the original data
original_hash = hashlib.sha224(data).digest()

#Get hash of the recovered data
recovered_hash = hashlib.sha224(result).digest()

print("Original hash:", original_hash)
print("Recovered hash:", recovered_hash)
print("Hashes match:", original_hash == recovered_hash)
print(data)
print(result)


#print(ida.assemble_bytes(res2))

#print(len(disp_result))

# total = 0
# total2 = 0
# for d in range(m):
#     total += len(disp_result[d].content)
#     total2 += sys.getsizeof(disp_result[d].content)
#     print("content",len(disp_result[d].content))
# #print(disp_result)

# print("total", total)
# print("total2", total2)
# print("data size",len(data))
# print("expected",len(data) / m * n)


#fragments = ida.split_bytes_v2(data, n, m)
#res = ida.merge_bytes_v2(fragments, n, m)
#fragments = ida.split_bytes_v0(data, n, m)
#result = ida.assemble_bytes(fragments)
#print(result)

