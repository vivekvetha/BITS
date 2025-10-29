# Matrix Multiplication Implementation
import time
import numpy as np
import multiprocessing as mp
from sequential import sequential_matrix_multiply
from parallel import parallel_matrix_multiply


def benchmark_matrix_multiplication(matrix_sizes=[256, 512, 1024], max_processes=None):
    """
    Benchmark both sequential and parallel matrix multiplication
    """
    if max_processes is None:
        max_processes = mp.cpu_count()

    for N in matrix_sizes:
        print(f"\n{'='*60}")
        print(f"BENCHMARKING MATRIX SIZE: {N}x{N}")
        print(f"{'='*60}")

        # Generate random matrices
        A = np.random.rand(N, N)
        B = np.random.rand(N, N)

        # Sequential execution
        print("Sequential Matrix Multiplication:")
        start_time = time.time()
        C_seq = sequential_matrix_multiply(A, B)
        sequential_time = time.time() - start_time
        print(f"  Time: {sequential_time:.4f} seconds")

        # Parallel execution
        print("\nParallel Matrix Multiplication:")
        print("-" * 40)

        best_time = float('inf')
        best_processes = 1
        best_speedup = 0
        best_efficiency = 0
        C_par = None

        for processes in range(2, max_processes + 1):
            start_time = time.time()
            C_par_current = parallel_matrix_multiply(A, B, processes)
            parallel_time = time.time() - start_time

            speedup = sequential_time / parallel_time
            efficiency = speedup / processes * 100

            if parallel_time < best_time:
                best_time = parallel_time
                best_processes = processes
                best_speedup = speedup
                best_efficiency = efficiency
                C_par = C_par_current

            print(f"  {processes:2d} processes: {parallel_time:.4f}s | "
                  f"Speedup: {speedup:.2f}x | Efficiency: {efficiency:.1f}%")

        # Summary
        print(f"\n{'='*40}")
        print(f"BEST PERFORMANCE:")
        print(f"  Processes: {best_processes}")
        print(f"  Time: {best_time:.4f} seconds")
        print(f"  Speedup: {best_speedup:.2f}x")
        print(f"  Efficiency: {best_efficiency:.1f}%")
        print(f"  Improvement: {((sequential_time - best_time) / sequential_time * 100):.1f}%")


if __name__ == "__main__":
    print("Matrix Multiplication Benchmark")
    print("Sequential vs Parallel Performance Comparison")

    # Run benchmarks
    benchmark_matrix_multiplication(matrix_sizes=[256])
