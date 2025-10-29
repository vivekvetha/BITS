#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define NUM_VOLUNTEERS 10

int main() {
    int donations[NUM_VOLUNTEERS];  // Array to store individual donations
    int total_donation = 0;  // Total funds collected

    // Set seed for random number generation
    srand(42);  // Fixed seed for reproducibility

    // Parallel region for donation collection
    #pragma omp parallel for reduction(+:total_donation)
    for (int i = 0; i < NUM_VOLUNTEERS; i++) {
        donations[i] = rand() % 100 + 1;  // Each volunteer collects between $1 and $100
        total_donation += donations[i];  // Parallel reduction
        printf("Volunteer %d collected: $%d\n", i, donations[i]);
    }

    // Print the final total donation amount
    printf("\nTotal Funds Raised: $%d\n", total_donation);

    return 0;
}