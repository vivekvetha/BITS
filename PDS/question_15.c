#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <math.h>

#define TERMS 10  // Number of terms in Taylor series

double x;            // Input angle in radians
double sin_x = 0.0;  // Result
pthread_mutex_t lock;
sem_t sem;

// Function to compute factorial
double factorial(int n) {
    double fact = 1;
    for (int i = 1; i <= n; i++)
        fact *= i;
    return fact;
}

// Thread function to compute Taylor series term
void* compute_term(void* arg) {
    int n = *(int*)arg;
    free(arg);

    // Compute the term (-1)^n * x^(2n+1) / (2n+1)!
    double term = pow(-1, n) * pow(x, 2 * n + 1) / factorial(2 * n + 1);

    sem_wait(&sem);  // Wait for turn

    // Protect the shared result variable using mutex
    pthread_mutex_lock(&lock);
    sin_x += term;
    pthread_mutex_unlock(&lock);

    sem_post(&sem);  // Signal next thread

    return NULL;
}

int main() {
    printf("Enter value of x (in radians): ");
    scanf("%lf", &x);

    pthread_t threads[TERMS];
    pthread_mutex_init(&lock, NULL);
    sem_init(&sem, 0, 1);  // Initialize semaphore

    // Create threads
    for (int i = 0; i < TERMS; i++) {
        int* n = malloc(sizeof(int));
        *n = i;
        pthread_create(&threads[i], NULL, compute_term, n);
    }

    // Join threads
    for (int i = 0; i < TERMS; i++)
        pthread_join(threads[i], NULL);

    pthread_mutex_destroy(&lock);
    sem_destroy(&sem);

    printf("Approximate sin(x): %lf\n", sin_x);
    printf("Actual sin(x): %lf\n", sin(x));

    return 0;
}