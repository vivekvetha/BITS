#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>

void *thread_function(void *arg) {
    // Thread code
    return (void *)42; // Example return value
}

int main() {
    pthread_t thread;
    void *result;

    // Create and start the thread
    pthread_create(&thread, NULL, thread_function, NULL);

    // Wait for the thread to finish
    pthread_join(thread, &result);

    // Thread has finished, do something with the result
    int return_value = (int)result;

    return 0;
}