#include <stdio.h>
#include <omp.h>

int main() {
    int x = 0;
    #pragma omp parallel for schedule(dynamic, 2)
    for (int i = 0; i < 10; i++) {
        printf("Thread %d: x = %d\n", omp_get_thread_num(), x);
        x++;
    }
}