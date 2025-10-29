#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define NUM_THREADS 2  // Number of slave threads (each handles a range)
#define NUM_DATA 1000   // Number of sensor data items

int main() {
    int data[NUM_DATA];   // Sensor data
    int histogram[NUM_THREADS] = {0}; // Histogram buckets
    int bucket_size = 100 / NUM_THREADS; // Bucket size

    // Generate random sensor data between 0-99
    srand(42);
    for (int i = 0; i < NUM_DATA; i++) {
        data[i] = rand() % 100;
    }

    // OpenMP Parallel Section
    #pragma omp parallel num_threads(NUM_THREADS)
    {
        int thread_id = omp_get_thread_num(); // Get thread rank
        int start = thread_id * bucket_size;          // Bucket start value
        int end = start + bucket_size - 1;                 // Bucket end value

        // Each thread processes its bucket range
        for (int i = 0; i < NUM_DATA; i++) {
            // printf("Thread %d: Data %d\n", thread_id, data[i]);
            if (data[i] >= start && data[i] <= end) {
                #pragma omp atomic
                histogram[thread_id]++;
            }
        }
    }


    // Master thread prints the histogram
    printf("\nHistogram Results:\n");
    for (int i = 0; i < NUM_THREADS; i++) {
        printf("Bucket %d-%d: %d\n", i * bucket_size, (i * bucket_size) + bucket_size - 1, histogram[i]);
    }

    return 0;
}