#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

// Global shared variable
int sharedVariable = 0;

// Mutex declaration
pthread_mutex_t myMutex;

void* threadFunction(void* arg) {
    for (int i = 0; i < 5; i++) {
        // Acquire the lock
        // pthread_mutex_lock(&myMutex);

        // Critical section (protected resource)
        sharedVariable++;
        printf("Thread %ld: Incremented sharedVariable to %d\n", (long)arg, sharedVariable);
        usleep(1000000);
        // Release the lock
        // pthread_mutex_unlock(&myMutex);

        // Simulate some work
        // Sleep for 100ms
    }

    return NULL;
}

int main() {
    pthread_t thread1, thread2;

    // Initialize the mutex
    pthread_mutex_init(&myMutex, NULL);

    // Create threads
    pthread_create(&thread1, NULL, threadFunction, (void*)1);
    pthread_create(&thread2, NULL, threadFunction, (void*)2);

    // Wait for threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    // Destroy the mutex
    pthread_mutex_destroy(&myMutex);

    return 0;
}
