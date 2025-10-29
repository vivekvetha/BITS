#include <stdio.h>
#include <pthread.h>

int num1, num2;
int sum, difference, product;

void* calculateSum(void* arg) {
    sum = num1 + num2;
    pthread_exit(NULL);
}

void* calculateDifference(void* arg) {
    difference = num1 - num2;
    pthread_exit(NULL);
}

void* calculateProduct(void* arg) {
    product = num1 * num2;
    pthread_exit(NULL);
}

int main() {
    pthread_t thread_sum, thread_difference, thread_product;

    printf("Enter two numbers: ");
    scanf("%d %d", &num1, &num2);

    pthread_create(&thread_sum, NULL, calculateSum, NULL);
    pthread_create(&thread_difference, NULL, calculateDifference, NULL);
    pthread_create(&thread_product, NULL, calculateProduct, NULL);

    pthread_join(thread_sum, NULL);
    pthread_join(thread_difference, NULL);
    pthread_join(thread_product, NULL);

    printf("Sum: %d\n", sum);
    printf("Difference: %d\n", difference);
    printf("Product: %d\n", product);

    return 0;
}