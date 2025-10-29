#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define TOTAL_CUSTOMERS 20  // More than 10 customers trying to buy
#define MAX_PURCHASES 10     // Only 10 successful purchases

pthread_mutex_t lock;  // Mutex for synchronization
int total_purchases = 0;  // Shared counter

void* try_to_buy(void* arg) {
    int customer_id = *(int*)arg;
    pthread_mutex_lock(&lock);  // Lock before modifying shared data

    if (total_purchases < MAX_PURCHASES) {
        total_purchases++;
        printf("Customer %d successfully bought the product! (Purchase #%d)\n", customer_id, total_purchases);
    } else {
        printf("Customer %d failed to buy the product. Offer is sold out!\n", customer_id);
    }

    pthread_mutex_unlock(&lock);  // Unlock after operation
    free(arg);  // Free dynamically allocated memory for thread argument
    return NULL;
}

int main() {
    pthread_t customers[TOTAL_CUSTOMERS];

    pthread_mutex_init(&lock, NULL);  // Initialize mutex

    // Create customer threads
    for (int i = 0; i < TOTAL_CUSTOMERS; i++) {
        int* customer_id = malloc(sizeof(int));
        *customer_id = i + 1;
        pthread_create(&customers[i], NULL, try_to_buy, customer_id);
    }

    // Wait for all threads to finish
    for (int i = 0; i < TOTAL_CUSTOMERS; i++) {
        pthread_join(customers[i+1], NULL);
    }

    pthread_mutex_destroy(&lock);  // Destroy mutex
    printf("Total purchases: %d\n", total_purchases);

    return 0;
}