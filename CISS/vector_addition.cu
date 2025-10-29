#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>

#define CHECK_CUDA(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            std::cerr << "CUDA error at line " << __LINE__ << ": " << cudaGetErrorString(err) << std::endl; \
            exit(1); \
        } \
    } while(0)

__global__ void add_vectors(double *a, double *b, double *c, int n) {
    int id = blockDim.x * blockIdx.x + threadIdx.x;

    if (id < n) {
        c[id] = a[id] + b[id];
    }
}

void cpu_vector_add(const std::vector<double>& a, const std::vector<double>& b, std::vector<double>& c, int n) {
    for (int i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}

void benchmark_vector_size(int N) {
    std::cout << "\n" << std::string(60, '=') << std::endl;
    std::cout << "BENCHMARKING VECTOR SIZE: " << N << " elements (" << (N * sizeof(double)) / (1024*1024) << " MB)" << std::endl;
    std::cout << std::string(60, '=') << std::endl;

    size_t bytes = N * sizeof(double);

    std::vector<double> h_A(N);
    std::vector<double> h_B(N);
    std::vector<double> h_C(N, 0.0);
    std::vector<double> h_C_cpu(N);

    // Initialize input vectors
    for (int i = 0; i < N; ++i) {
        h_A[i] = 1.0;
        h_B[i] = 2.0;
    }

    // Allocate GPU memory
    double *d_A, *d_B, *d_C;
    CHECK_CUDA(cudaMalloc(&d_A, bytes));
    CHECK_CUDA(cudaMalloc(&d_B, bytes));
    CHECK_CUDA(cudaMalloc(&d_C, bytes));

    // Copy data to GPU
    CHECK_CUDA(cudaMemcpy(d_A, h_A.data(), bytes, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(d_B, h_B.data(), bytes, cudaMemcpyHostToDevice));

    // Launch configuration
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    std::cout << "Launch config: " << blocksPerGrid << " blocks x " << threadsPerBlock << " threads" << std::endl;

    // Create timing events
    cudaEvent_t start, stop;
    CHECK_CUDA(cudaEventCreate(&start));
    CHECK_CUDA(cudaEventCreate(&stop));

    // Launch kernel with timing
    CHECK_CUDA(cudaEventRecord(start));
    add_vectors<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);
    CHECK_CUDA(cudaGetLastError());
    CHECK_CUDA(cudaDeviceSynchronize());
    CHECK_CUDA(cudaEventRecord(stop));
    CHECK_CUDA(cudaEventSynchronize(stop));

    float gpu_kernel_time_ms = 0;
    CHECK_CUDA(cudaEventElapsedTime(&gpu_kernel_time_ms, start, stop));

    // Copy result back to host
    CHECK_CUDA(cudaMemcpy(h_C.data(), d_C, bytes, cudaMemcpyDeviceToHost));

    // CPU timing
    auto start_cpu = std::chrono::high_resolution_clock::now();
    cpu_vector_add(h_A, h_B, h_C_cpu, N);
    auto stop_cpu = std::chrono::high_resolution_clock::now();
    auto cpu_time_ms = std::chrono::duration_cast<std::chrono::microseconds>(stop_cpu - start_cpu).count() / 1000.0;

    bool success = true;
    double tolerance = 1.0e-14;

    for (int i = 0; i < std::min(100, N); ++i) {
        if (std::abs(h_C[i] - 3.0) > tolerance) {
            success = false;
            break;
        }
    }
    for (int i = std::max(0, N-100); i < N && success; ++i) {
        if (std::abs(h_C[i] - 3.0) > tolerance) {
            success = false;
            break;
        }
    }

    // Results
    if (success) {
        std::cout << "Vector Addition Successful!" << std::endl;
        std::cout << "CPU Execution Time: " << cpu_time_ms << " ms" << std::endl;
        std::cout << "GPU Kernel Execution Time: " << gpu_kernel_time_ms << " ms" << std::endl;

        if (gpu_kernel_time_ms > 0) {
            double speedup = cpu_time_ms / gpu_kernel_time_ms;
            double throughput = (N / 1e6) / (gpu_kernel_time_ms / 1000.0);
            std::cout << "GPU Speedup: " << speedup << "x" << std::endl;
            std::cout << "GPU Throughput: " << throughput << " M elements/sec" << std::endl;
        }
    } else {
        std::cout << "Vector Addition Failed!" << std::endl;
    }

    // Cleanup
    CHECK_CUDA(cudaFree(d_A));
    CHECK_CUDA(cudaFree(d_B));
    CHECK_CUDA(cudaFree(d_C));
    CHECK_CUDA(cudaEventDestroy(start));
    CHECK_CUDA(cudaEventDestroy(stop));
}

int main() {
    // Test multiple vector sizes
    std::vector<int> sizes = {
        1 << 20,
        1 << 22,
        1 << 24,
        1 << 26,
        1 << 28
    };

    for (int size : sizes) {
        benchmark_vector_size(size);
    }

    return 0;
}
