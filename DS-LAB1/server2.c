#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 5002
#define BUF_SIZE 1024

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUF_SIZE];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) { perror("bind"); exit(1); }
    if (listen(server_fd, 5) < 0) { perror("listen"); exit(1); }

    printf("SERVER2 listening on port %d...\n", PORT);

    while (1) {
        new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen);
        if (new_socket < 0) { perror("accept"); continue; }

        memset(buffer, 0, BUF_SIZE);
        read(new_socket, buffer, BUF_SIZE);
        buffer[strcspn(buffer, "\n")] = 0; // remove newline

        printf("SERVER2 received file request: %s\n", buffer);

        FILE *fp = fopen(buffer, "r");
        if (!fp) {
            char *msg = "NOT_FOUND";
            write(new_socket, msg, strlen(msg));
            printf("SERVER2: File not found.\n");
        } else {
            char filebuf[BUF_SIZE];
            size_t n;
            while ((n = fread(filebuf, 1, BUF_SIZE, fp)) > 0) {
                write(new_socket, filebuf, n);
            }
            fclose(fp);
            printf("SERVER2: File sent successfully.\n");
        }

        close(new_socket);
    }
    return 0;
}