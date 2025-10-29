# Sequential Matrix Multiplication Implementation
import numpy as np

def sequential_matrix_multiply(A, B):
    """
    Performs sequential matrix multiplication.
    Assumes A and B are square NumPy arrays of the same size.
    """
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    return C
