#include <stdio.h>
#include <omp.h>

#define size 100

int main() {
    int arr[size];
    int sum = 0;

    for (int i = 0; i < size; i++) {
        arr[i] = i + 1;
    }

    #pragma omp parallel for reduction(+:sum)
    for (int i =0; i < size; i++) {
        int thread_id = omp_get_thread_num();
        int num_threads = omp_get_num_threads();
        sum += arr[i];
        printf("Hello World - Thread %d of %d: sum %d \n", thread_id, num_threads, sum);
    }

    printf("Sum of the elements: %d\n", sum);
}