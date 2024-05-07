from drex.utils.reliability.utils import *
from drex.utils.reliability.fragment_handler import fragment_writer, fragment_reader, fragment_reader_bytes
import pickle
import numpy as np
import time
import itertools


class Fragment:
    def __init__(self, idx, content, p, n, m):
        self.idx = idx
        self.content = content
        self.p = p
        self.n = n
        self.m = m


def split_bytes(data, n, m):
    """
    Inputs:
    data: bytes to split
    n   : number of fragments after splitting the file
    m   : minimum number of fragments required to restore the file
    Output:
    a list of n fragments (as Fragment objects)
    """
    # print(len(data))
    # data = pickle.dumps(data)
    print(len(data))

    if n < 0 or m < 0:
        raise ValueError("numFragments ad numToAssemble must be positive.")

    if m > n:
        raise ValueError("numToAssemble must be less than numFragments")

    # find the prime number greater than n
    # all computations are done modulo p
    p = 257 if n < 257 else nextPrime(n)

    array_data = np.frombuffer(data, dtype=np.uint8)
    del data
    top_index = len(array_data) - (len(array_data) % m)
    original_segments_arr = array_data[:top_index].reshape(-1, m)
    last_segment = array_data[top_index:]

    # fill with zeros to complete the last segment
    if len(last_segment) < m:
        last_segment = np.pad(
            last_segment, (0, m - len(last_segment)), 'constant')

    del array_data

    # insert last segment into grouped array
    original_segments_arr = np.vstack([original_segments_arr, last_segment])

    # print("Original",original_segments_arr)

    building_blocks = build_building_blocks(m, n, p)

    # array_data = np.frombuffer(data, dtype=np.uint8)
    # grouped_array = array_data.reshape(-1, m)
    # print(grouped_array)

    # original_segments = list(itertools.zip_longest(*(iter(data),) * m, fillvalue=0))
    # print(original_segments)

    # print(len(original_segments))
    # original_segments_arr = np.array(original_segments)
    # print(original_segments_arr.shape)
    # building_blocks = build_building_blocks(m,n,p)
    fragments = []

    for i in range(n):
        fragment_arr = (building_blocks[i] @ original_segments_arr.T) % p
        print(fragment_arr)
        print(len(fragment_arr))
        frag = Fragment(i, fragment_arr, p, n, m)
        fragments.append(frag)

    return fragments


def split_bytes_v1(data, n, m):
    k = 8
    field = 2 ** k - 1
    matrix = generate_vandermode(m, n, field)
    print(matrix)
    base_alpha = generate_field(field, k)
    Tabla_Alphas, LAlphas = Generar_Alphas(m, field, base_alpha)

    in_file = open("data.txt", "rb")
    if in_file is None:
        print("no se puede abrir o el archivo no existe")
        return

    Salidas = []
    BufferArchivo = [0] * m

    try:
        for i in range(n):
            Buffernombre = "D" + str(i)
            Salida = open(Buffernombre, "wb")
            if Salida is None:
                print("no se puede crear los dispersos")
                return
            Salidas.append(Salida)

            # Procesamiento 2 - service time
            valor = 48
            Salida.write(bytes([valor]))
            Salida.write(bytes([n]))
            Salida.write(bytes([m]))
            for j in range(m):
                valor = matrix[i][j]
                print(valor)
                Salida.write(bytes([int(valor)]))

        # Lectura 1 - read time
        Simbolos = 0
        bandera = 0
        for x in range(len(data)):

            for i in range(m):
                BufferArchivo[i] = 0

            for i in range(m):
                valor = in_file.read(1)
                # print("Valor",valor)
                if not valor:
                    break
                valor = abs(int.from_bytes(valor, byteorder='little'))
                BufferArchivo[i] = valor
                Simbolos += 1
                bandera += 1

            if bandera != 0:
                # GEnERAR DISPERSOS
                for i in range(n):
                    aux = 0
                    for j in range(m):
                        aux = Suma_Resta(aux, Multiplicacion(Tabla_Alphas, LAlphas, field,
                                                             matrix[i][j], BufferArchivo[j]))
                    valor = aux
                    Salidas[i].write(bytes([valor]))

        valor = Simbolos % m
        for i in range(n):
            Salidas[i].seek(0)
            Salidas[i].write(bytes([valor]))
    finally:
        in_file.close()
        for salida in Salidas:
            salida.close()

        # Clean up
        # for i in range(n):
        #    os.remove("D" + str(i))


def split_bytes_v2(data, n, m):
    data_len = len(data)
    results = []

    print(data)

    for d in data:
        print(int(d))

    # Create an empty array of shape (n, m)
    matrix = np.empty((n, m))
    print(data_len // m)
    result_matrix = np.empty((n, data_len // m))

    # Use vectorized operations to calculate the values
    for i in range(n):
        for j in range(m):
            matrix[i][j] = np.power(1 + i, j)

    print(matrix)

    for i in range(n):
        for j in range(data_len // m):
            for k in range(m):
                result_matrix[i][j] += matrix[i][k] * data[j * m + k]
    """#print(result_matrix)

    i_values = np.arange(n).reshape(-1, 1)
    j_values = np.arange(m)

    matrix = np.power(1 + i_values, j_values)

    print(result_matrix)

    print(matrix)"""
    print(result_matrix)
    return result_matrix


def split_bytes_v3(data, n, m):
    # Generate random coefficients for encoding
    import random
    coefficients = [random.randint(1, 255) for _ in range(m - 1)]
    encoded_chunks = []
    
    # Encode data into chunks
    for i in range(n):
        chunk = bytearray(len(data))
        for j, byte in enumerate(data):
            value = byte
            for k in range(m - 1):
                value += coefficients[k] * (i + 1) ** (k + 1)
            chunk[j] = value % 256
        encoded_chunks.append(chunk)
    
    return encoded_chunks

    

def recovery(f_list, vander_matrix, m=4, n=8):
    vander_inv = np.linalg.inv(vander_matrix)
    M = vander_inv @ f_list
    print(M)
    for x in M:
        integer_value = int(x)
        print(integer_value.to_bytes((integer_value.bit_length() + 7) // 8, 'big'))
    return M
            
def merge_bytes_v2(data, n, m):
    size = len(data[0])
    a = np.zeros((m, m))
    ia = np.zeros((m, m))
    dm = np.zeros(size)
    
    print(dm)
    
    for i in range(m):
        for j in range(m):
            a[i][j] = (i + 1) ** j
    
    print(a)
    ia = np.linalg.inv(a)
    print(ia)

    for i in range(size):
        for j in range (m):
            dm[i] += ia[i%m][j] * data[j][int(i/m)]

    print(dm)
    
    

def split_bytes_v0(data, n, m):
    """
    Inputs: 
    data: bytes to split
    n   : number of fragments after splitting the file
    m   : minimum number of fragments required to restore the file
    Output:
    a list of n fragments (as Fragment objects)
    """
    # print(data)
    # data = pickle.dumps(data)
    # print(data)

    if n < 0 or m < 0:
        raise ValueError("numFragments ad numToAssemble must be positive.")

    if m > n:
        raise ValueError("numToAssemble must be less than numFragments")

    # find the prime number greater than n
    # all computations are done modulo p
    p = 257 if n < 257 else nextPrime(n)

    start = time.time_ns()
    original_segments = list(itertools.zip_longest(
        *(iter(data),) * m, fillvalue=0))
    end = time.time_ns()

    # for the last subfile, if the length is less than m, pad the subfile with zeros
    # to achieve final length of m
    # residue = len(data)%m
    # if residue:
    #    last_subfile=[data[i] for i in range(len(data)-residue,len(data))]
    #    last_subfile.extend([0]*(m-residue))
    #    original_segments.append(tuple(last_subfile))
    #     #last_subfile.extend([0]*(m-residue))

    building_blocks = build_building_blocks(m, n, p)
    print("Original", original_segments)
    fragments = []
    for i in range(n):
        fragment_arr = np.array([inner_product(
            building_blocks[i], original_segments[k], p) for k in range(len(original_segments))])
        # print(sys.getsizeof(fragment_arr))
        # fragment = []
        # for k in range(len(original_segments)):
        #    fragment.append(inner_product(building_blocks[i], original_segments[k],p))
        # print(fragment)
        # print(sys.getsizeof(fragment))
        frag = Fragment(i, fragment_arr, p, n, m)
        fragments.append(frag)

    return fragments


def split(filename, n, m):
    """
    Inputs: 
    file: name of the file to split
    n   : number of fragments after splitting the file
    m   : minimum number of fragments required to restore the file
    Output:
    a list of n fragments (as Fragment objects)
    """
    if n < 0 or m < 0:
        raise ValueError("numFragments ad numToAssemble must be positive.")

    if m > n:
        raise ValueError("numToAssemble must be less than numFragments")

    # find the prime number greater than n
    # all computations are done modulo p
    p = 257 if n < 257 else nextPrime(n)

    # convert file to byte strings
    original_file = open(filename, "rb").read()

    # split original_file into chunks (subfiles) of length m
    original_segments = [list(original_file[i:i+m])
                         for i in range(0, len(original_file), m)]

    # for the last subfile, if the length is less than m, pad the subfile with zeros
    # to achieve final length of m
    residue = len(original_file) % m
    if residue:

        last_subfile = original_segments[-1]
        last_subfile.extend([0]*(m-residue))

    building_blocks = build_building_blocks(m, n, p)

    fragments = []
    for i in range(n):
        fragment = []
        for k in range(len(original_segments)):
            fragment.append(inner_product(
                building_blocks[i], original_segments[k], p))
        fragments.append(fragment)

    return fragment_writer(filename, n, m, p, original_file, fragments)


def assemble_bytes(fragments, output_filename=None):
    '''
    Input: 
    fragments : a list of fragments (as Fragment objects)
    output_filename: a String for the name of the file to write
    Output: 
    String represents the content of the original file
    If filename is given, the content is written to the file
    '''

    (m, n, p, fragments) = fragment_reader_bytes(fragments)
    building_basis = []
    fragments_matrix = []
    for (idx, fragment) in fragments:
        print(fragment)
        building_basis.append(idx)
        fragments_matrix.append(fragment)

    inverse_building_matrix = vandermonde_inverse(building_basis, p)

    output_matrix = matrix_product(
        inverse_building_matrix, fragments_matrix, p)

    # each column of output matrix is a chunk of the original matrix
    original_segments = []
    ncol = len(output_matrix[0])
    nrow = len(output_matrix)
    for c in range(ncol):
        col = [output_matrix[r][c] for r in range(nrow)]
        original_segments.append(col)

    # remove tailing zeros of the last segment
    last_segment = original_segments[-1]
    while last_segment[-1] == 0:
        last_segment.pop()

    # combine the original_segment into original_file
    original_file = []
    for segment in original_segments:
        original_file.extend(segment)

    # convert original_file to its content
    original_file_content = bytes(original_file)
    # data = pickle.loads(original_file_content)

    return original_file_content


def assemble(fragments_filenames, output_filename=None):
    '''
    Input: 
    fragments_filenames : a list of fragments filenames
    output_filename: a String for the name of the file to write
    Output: 
    String represents the content of the original file
    If filename is given, the content is written to the file
    '''

    (m, n, p, fragments) = fragment_reader(fragments_filenames)
    building_basis = []
    fragments_matrix = []
    for (idx, fragment) in fragments:
        building_basis.append(idx)
        fragments_matrix.append(fragment)

    inverse_building_matrix = vandermonde_inverse(building_basis, p)

    output_matrix = matrix_product(
        inverse_building_matrix, fragments_matrix, p)

    # each column of output matrix is a chunk of the original matrix
    original_segments = []
    ncol = len(output_matrix[0])
    nrow = len(output_matrix)
    for c in range(ncol):
        col = [output_matrix[r][c] for r in range(nrow)]
        original_segments.append(col)

    # remove tailing zeros of the last segment
    last_segment = original_segments[-1]
    while last_segment[-1] == 0:
        last_segment.pop()

    # combine the original_segment into original_file
    original_file = []
    for segment in original_segments:
        original_file.extend(segment)

    # convert original_file to its content
    original_file_content = "".join(list(map(chr, original_file)))

    if output_filename:  # write the output to file
        with open(output_filename, 'wb') as fh:
            fh.write(bytes(original_file))

        print("Generated file {}".format(output_filename))
        return
    else:
        return original_file_content
