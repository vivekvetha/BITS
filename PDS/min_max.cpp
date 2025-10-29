#include <stdio.h>
#include <unistd.h>

int max(int arr[], int size) {
    int max_val = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] > max_val) {
            max_val = arr[i];
        }
    }
    return max_val;
}

int min(int arr[], int size) {
    int min_val = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] < min_val) {
            min_val = arr[i];
        }
    }
    return min_val;
}

int main() {
    pid_t pid;
    int numbers[] = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};
    int num_count = sizeof(numbers) / sizeof(numbers[0]);

    pid = fork();

    if (pid < 0) {
        fprintf(stderr, "Fork failed\n");
        return 1;
    } else if (pid == 0) {
        // This code is executed by the child process

        int min_val = min(numbers, num_count);
        printf("Child process. Minimum value: %d\n", min_val);
    } else {
        // This code is executed by the parent process

        int max_val = max(numbers, num_count);
        printf("Parent process. Maximum value: %d\n", max_val);
    }

    return 0;
}