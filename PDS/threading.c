#include <stdio.h>
#include <pthread.h>
#include <stdlib.h> // Added for atoi

void *thread_func(void *arg) {
    int thread_id = *((int *)arg);
    printf("Thread %d: Hello from Thread %d!\n", thread_id, thread_id);
    return NULL;
}

int main() {
    int num_threads;

    printf("Enter the number of threads to create: ");
    scanf("%d", &num_threads);

    if (num_threads <= 0) {
        fprintf(stderr, "Invalid number of threads. Please provide a positive integer.\n");
        return 1;
    }

    pthread_t threads[num_threads];

    for (int i = 0; i < num_threads; i++) {
        if (pthread_create(&threads[i], NULL, thread_func, (void *)&i) != 0) {
            fprintf(stderr, "Error creating thread %d\n", i);
            return 1;
        }
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}