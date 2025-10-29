#include <stdio.h>
#include <omp.h>

#define M 10
#define N 4

int matrix[M][N], vector[N], result[M];

int main() {
    // Initialize matrix & vector
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++)
            matrix[i][j] = i + j;

    for (int j = 0; j < N; j++)
        vector[j] = 1;

    #pragma omp parallel for
    for (int i = 0; i < M; i++) {
        int thread_id = omp_get_thread_num();
        result[i] = 0;
        for (int j = 0; j < N; j++) {
            result[i] += matrix[i][j] * vector[j];
            printf("Thread %d \n", thread_id);
        }
    }

    // Print result
    for (int i = 0; i < M; i++) {
        printf("Row %d: %d\n", i, result[i]);
    }
    return 0;
}