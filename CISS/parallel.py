# Parallel Matrix Multiplication Implementation
import numpy as np
import multiprocessing as mp

def worker_pure_multiply(args):
    """
    Worker function that performs pure matrix multiplication for a chunk of rows.
    """
    start_row, end_row, A, B = args
    n = A.shape[0]
    result = np.zeros((end_row - start_row, n))
    for i in range(start_row, end_row):
        for j in range(n):
            for k in range(n):
                result[i - start_row, j] += A[i, k] * B[k, j]
    return result


def parallel_matrix_multiply(A, B, num_processes):
    """
    Performs parallel matrix multiplication using multiprocessing.
    """
    n = A.shape[0]
    chunk_size = n // num_processes

    # Create work items for each process
    work_items = []
    for i in range(num_processes):
        start_row = i * chunk_size
        end_row = start_row + chunk_size if i < num_processes - 1 else n
        work_items.append((start_row, end_row, A, B))

    with mp.Pool(processes=num_processes) as pool:
        result_chunks = pool.map(worker_pure_multiply, work_items)

    # Concatenate the results from all processes
    C = np.vstack(result_chunks)
    return C
