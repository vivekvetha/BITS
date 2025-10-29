#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 5001
#define BUF_SIZE 1024

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) { perror("Socket creation"); exit(1); }

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // SERVER1

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connect error");
        exit(1);
    }

    char filename[BUF_SIZE];
    printf("Enter filename: ");
    fgets(filename, BUF_SIZE, stdin);
    filename[strcspn(filename, "\n")] = 0;  // remove newline

    write(sock, filename, strlen(filename));

    printf("Response from SERVER1:\n");

    char buffer[BUF_SIZE];
    int n;
    while ((n = read(sock, buffer, BUF_SIZE - 1)) > 0) {
        buffer[n] = '\0';
        printf("%s", buffer);
    }

    close(sock);
    return 0;
}