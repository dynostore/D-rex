from pyfinite import ffield
import numpy as np

def rabin_encode(data, n, k):
    # Define the finite field GF(256)
    field = ffield.FField(8)

    # Convert bytes object to a list of integers
    data_int = list(data)

    # Create a Vandermonde matrix for encoding
    A = np.zeros((k, k), dtype=int)
    for i in range(k):
        for j in range(k):
            A[i, j] = field.Multiply(field.generator, (i * j))  # Utilize multiplication without modulo

    # Encode the data
    encoded_data = []
    for i in range(0, len(data_int), k):
        chunk = data_int[i:i+k]
        if len(chunk) < k:
            # If the last chunk is smaller than k, pad it with zeros
            chunk += [0] * (k - len(chunk))
        encoded_chunk = np.dot(chunk, A) % 256  # Use 256 as modulus for GF(256)
        encoded_data.append(encoded_chunk)

    # Split the encoded data into n segments
    segment_size = len(encoded_data) // n
    segments = [encoded_data[i * segment_size: (i + 1) * segment_size] for i in range(n)]

    return segments

# Example usage
data = b'Your bytes data goes here'
n = 5  # Total number of segments
k = 3  # Threshold number of segments required for reconstruction

segments = rabin_encode(data, n, k)
