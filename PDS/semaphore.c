#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>

#define SIZE 10
#define NUM_THREADS 2

int sharedArray[SIZE];
sem_t semaphore;

void* threadFunction(void* arg) {
    int threadID = *(int*)arg;

    for (int i = 0; i < SIZE; i++) {
        // Wait on the semaphore
        sem_wait(&semaphore);

        // Critical section: Access shared resource (sharedArray)
        sharedArray[i] = threadID;

        // Release the semaphore
        sem_post(&semaphore);
    }

    pthread_exit(NULL);
}

int main() {
    pthread_t threads[NUM_THREADS];
    int threadIDs[NUM_THREADS];

    // Initialize semaphore
    sem_init(&semaphore, 0, 1); // Initial value of semaphore is 1

    for (int i = 0; i < NUM_THREADS; i++) {
        threadIDs[i] = i;
        pthread_create(&threads[i], NULL, threadFunction, (void*)&threadIDs[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Display the shared array
    for (int i = 0; i < SIZE; i++) {
        printf("%d ", sharedArray[i]);
    }
    printf("\n");

    // Destroy semaphore
    sem_destroy(&semaphore);

    return 0;
}