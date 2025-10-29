#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT1 5001
#define SERVER2_PORT 5002
#define BUF_SIZE 1024

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address, serv_addr;
    int addrlen = sizeof(address);
    char buffer[BUF_SIZE];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT1);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) { perror("bind"); exit(1); }
    if (listen(server_fd, 5) < 0) { perror("listen"); exit(1); }

    printf("SERVER1 listening on port %d...\n", PORT1);

    while (1) {
        new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen);
        if (new_socket < 0) { perror("accept"); continue; }

        memset(buffer, 0, BUF_SIZE);
        read(new_socket, buffer, BUF_SIZE);
        buffer[strcspn(buffer, "\n")] = 0;
        printf("SERVER1 received file request: %s\n", buffer);

        // Step 1: Read local file
        char local_content[BUF_SIZE] = {0};
        FILE *fp1 = fopen(buffer, "r");
        int local_found = 0;
        if (fp1) {
            fread(local_content, 1, BUF_SIZE, fp1);
            fclose(fp1);
            local_found = 1;
            printf("SERVER1: Found file locally.\n");
        } else {
            printf("SERVER1: File not found locally.\n");
        }

        // Step 2: Request file from SERVER2
        char server2_content[BUF_SIZE] = {0};
        int server2_found = 0;

        int sock2 = socket(AF_INET, SOCK_STREAM, 0);
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(SERVER2_PORT);
        serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // adjust if on another server

        if (connect(sock2, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == 0) {
            write(sock2, buffer, strlen(buffer));
            int n = read(sock2, server2_content, BUF_SIZE - 1);
            if (n > 0) {
                server2_content[n] = '\0';
                if (strcmp(server2_content, "NOT_FOUND") == 0) {
                    server2_found = 0;
                    printf("SERVER1: File not found on SERVER2.\n");
                } else {
                    server2_found = 1;
                    printf("SERVER1: Received file from SERVER2.\n");
                }
            }
            close(sock2);
        } else {
            printf("SERVER1: Could not connect to SERVER2.\n");
        }

        // Step 3: Compare and send to client
        if (!local_found && !server2_found) {
            char *msg = "File not found on SERVER1 or SERVER2.\n";
            write(new_socket, msg, strlen(msg));
        } else if (local_found && server2_found) {
            if (strcmp(local_content, server2_content) == 0) {
                char *msg = "SERVER1: Both servers have identical file. Sending file...\n";
                write(new_socket, msg, strlen(msg));
                write(new_socket, local_content, strlen(local_content));
            } else {
                char *msg = "SERVER1: File differs between servers. Sending both versions...\n---SERVER1 VERSION---\n";
                write(new_socket, msg, strlen(msg));
                write(new_socket, local_content, strlen(local_content));
                write(new_socket, "\n---SERVER2 VERSION---\n", 23);
                write(new_socket, server2_content, strlen(server2_content));
            }
        } else if (local_found) {
            char *msg = "SERVER1: File only found locally. Sending file...\n";
            write(new_socket, msg, strlen(msg));
            write(new_socket, local_content, strlen(local_content));
        } else {
            char *msg = "SERVER1: File only found on SERVER2. Sending file...\n";
            write(new_socket, msg, strlen(msg));
            write(new_socket, server2_content, strlen(server2_content));
        }

        close(new_socket);
    }

    return 0;
}