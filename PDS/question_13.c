#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <float.h>  // For DBL_MAX and DBL_MIN

int main(int argc, char** argv) {
    int rank, num_procs;
    double local_min_temp, local_max_temp;
    double global_min_temp, global_max_temp;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

    // Simulating temperature data (Each process gets different random temperatures)
    srand(rank + 1);
    local_min_temp = (rand() % 100) + 10.0;  // Random temp between 10-110
    local_max_temp = local_min_temp + (rand() % 20);  // Max is slightly higher than min

    printf("Process %d: Local Min = %.2f, Local Max = %.2f\n", rank, local_min_temp, local_max_temp);

    // Reduce local min/max to compute global min/max
    MPI_Reduce(&local_min_temp, &global_min_temp, 1, MPI_DOUBLE, MPI_MIN, 0, MPI_COMM_WORLD);
    MPI_Reduce(&local_max_temp, &global_max_temp, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    // Rank 0 prints the final global results
    if (rank == 0) {
        printf("\nGlobal Min Temperature: %.2f\n", global_min_temp);
        printf("Global Max Temperature: %.2f\n", global_max_temp);
    }

    MPI_Finalize();
    return 0;
}