#include <stdio.h>
#include <unistd.h>

int main() {
    pid_t pid; // Variable to store the process ID

    // Fork a new process
    pid = fork();

    if (pid < 0) {
        fprintf(stderr, "Fork failed\n");
        return 1;
    } else if (pid == 0) {
        // This code is executed by the child process

        printf("Child process. PID: %d\n", getpid());
    } else {
        // This code is executed by the parent process

        printf("Parent process. Child PID: %d\n", pid);
    }

    return 0;
}
