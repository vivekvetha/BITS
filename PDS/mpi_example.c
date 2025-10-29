#include <stdio.h>
#include <string.h>
#include <mpi.h>


int main(int argc, char *argv[]) {
    int rank, size;
    char message[100];

    // Initialize MPI
    MPI_Init(&argc, &argv);

    // Get the rank (process ID)
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Get the total number of processes
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (rank == 0) {
        // Process 0 sends a message to process 1
        sprintf(message, "Hello from process %d!", rank);
        MPI_Send(message, strlen(message)+1, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
    } else if (rank == 1) {
        // Process 1 receives the message from process 0
        MPI_Recv(message, 100, MPI_CHAR, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Received message: %s\n", message);
    }

    // Finalize MPI
    MPI_Finalize();

    return 0;
}