
def split_data(data, block_size=128*1024*1024):  # 128 MB in bytes
    """
    Split data into blocks of 128MB maximum
    """
    blocks = []
    block_num = 0
    offset = 0
    total_size = 0
    while offset < len(data):
        block = data[offset:offset+block_size]
        
        #Store the block three times for replication
        blocks.append({"block_num": block_num, "block": block})
        blocks.append({"block_num": block_num, "block": block})
        blocks.append({"block_num": block_num, "block": block})
        
        offset += block_size
        block_num += 1
        total_size += (len(block) * 3)
    return blocks, total_size
    
def split_data_hdfs_rs(data, size_to_stores):
    """
    Split data into blocks like it was decided by hdfs RS
    """
    blocks = []
    block_num = 0
    offset = 0
    total_size = 0
    
    for i in range(0, len(size_to_stores)):
        block_size = round(size_to_stores[i])
        print("block_size:", block_size)
        block = data[offset:offset+block_size]
        
        #Store the block one time only
        blocks.append({"block_num": block_num, "block": block})
        
        offset += block_size
        block_num += 1
        total_size += len(block)
    return blocks, total_size
