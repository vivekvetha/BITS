#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

// Task structure (Linked List Node)
typedef struct Task {
    int id;
    struct Task* next;
} queue;

queue* task_queue = NULL;  // Head of the task queue
pthread_mutex_t queue_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t task_cond = PTHREAD_COND_INITIALIZER;
int done = 0;  // Global flag to signal completion

void add_task(int id) {
    queue* new_task = (queue*)malloc(sizeof(queue));
    new_task->id = id;
    new_task->next = NULL;

    pthread_mutex_lock(&queue_mutex);

    if (!task_queue) {
        task_queue = new_task;
    } else {
        queue* temp = task_queue;
        while (temp->next) {
            temp = temp->next;
            temp->next = new_task;
        }
    }
    pthread_cond_signal(&task_cond); // Wake up one worker
    pthread_mutex_unlock(&queue_mutex);
}

// Worker thread function
void* worker_thread(void* arg) {
    int thread_id = *(int*)arg;
    free(arg);

    while (1) {
        pthread_mutex_lock(&queue_mutex);

        while (!task_queue && !done) {
            printf("Worker %d going to conditional wait\n", thread_id);
            pthread_cond_wait(&task_cond, &queue_mutex);  // Sleep if no tasks
        }

        if (done && !task_queue) {
            pthread_mutex_unlock(&queue_mutex);
            break; // Exit if no more tasks
        }

        // Get a task from the queue
        queue* task = task_queue;
        if (task_queue) {
            task_queue = task_queue->next;
        }

        pthread_mutex_unlock(&queue_mutex);

        if (task) {
            printf("Worker %d processing task %d\n", thread_id, task->id);
            free(task);
            sleep(10); // Simulating task execution
        }
    }
    printf("Worker %d exiting\n", thread_id);
    return NULL;
}

// Main function
int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <num_workers>\n", argv[0]);
        return 1;
    }
    int num_workers = atoi(argv[1]);
    if (num_workers <= 0) {
        printf("Error: Number of workers must be positive.\n");
        return 1;
    }
    pthread_t workers[num_workers];

    // Create worker threads
    for (int i = 0; i < num_workers; i++) {
        int* thread_id = malloc(sizeof(int));
        *thread_id = i;
        pthread_create(&workers[i], NULL, worker_thread, thread_id);
    }

    // Main thread generating tasks
    for (int i = 0; i < 30; i++) {
        add_task(i);
        sleep(10); // Simulate time between task arrivals
    }

    // Signal completion and wake all workers
    pthread_mutex_lock(&queue_mutex);
    done = 1;
    pthread_cond_broadcast(&task_cond); // Wake all threads for shutdown
    pthread_mutex_unlock(&queue_mutex);

    // Join worker threads
    for (int i = 0; i < num_workers; i++) {
        pthread_join(workers[i], NULL);
    }

    printf("All tasks completed. Exiting program.\n");
    return 0;
}