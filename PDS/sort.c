#include <stdio.h>
#include <omp.h>

void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void oddEvenSort(int arr[], int n) {
    int phase, i;
    #pragma omp parallel private(i, phase)
    for (phase = 0; phase < n; phase++) {
        if (phase % 2 == 0) {
            #pragma omp for
            for (i = 1; i < n; i += 2) {
                if (arr[i-1] > arr[i]) {
                    swap(&arr[i-1], &arr[i]);
                }
            }
        } else {
            #pragma omp for
            for (i = 1; i < n-1; i += 2) {
                if (arr[i] > arr[i+1]) {
                    swap(&arr[i], &arr[i+1]);
                }
            }
        }
    }
}

int main() {
    int arr[] = {9, 7, 5, 11, 12, 2, 14, 3, 10, 6};
    int n = sizeof(arr) / sizeof(arr[0]);

    printf("Original array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    oddEvenSort(arr, n);

    printf("Sorted array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    return 0;
}