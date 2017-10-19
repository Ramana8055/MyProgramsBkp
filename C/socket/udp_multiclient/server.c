#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

typedef int socket_t;

socket_t udps_init(char *ifaddr, uint16_t port, int *size)
{
    socket_t sock;
    int ret = -1;
    int opt = 1;
    struct sockaddr_in addr = {0};

    if (inet_pton(AF_INET, ifaddr, &(addr.sin_addr)) == 0) {
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        *size = sizeof(addr);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        return ret;
    }

    ret = setsockopt(sock,
                     SOL_SOCKET,
                     SO_REUSEADDR,
                     &opt,
                     sizeof(opt));
    if (ret < 0) {
        goto close_sock;
    }

    ret = bind(sock, (struct sockaddr *)&addr, sizeof(addr));
    if (ret < 0) {
        goto close_sock;
    }

    return sock;
close_sock:
    close(sock);
    return ret;
}


int main()
{
    socket_t sock;
    int size;
    int ret;
    char buf[32];

    int len = sizeof(struct sockaddr_in);

    sock = udps_init("127.0.0.1", 1234, &size);
    if (sock < 0) {
        fprintf(stderr, "OPEN\n");
        perror("Here:\n");
        return -1;
    }

    while (1) {
        memset(buf, 0, 32);
        ret = recvfrom(sock, buf, sizeof(buf), 0, NULL, &len);
        if (ret < 0) {
            fprintf(stderr, "Exit at %d\n", __LINE__);
            return -1;
        }
        fprintf(stderr, "Received %s\n", buf);
        ret = sendto(sock, "HELLO", 6, 0, 0, 0);
        if (ret < 0) {
            fprintf(stderr, "Exit at %d\n", __LINE__);
            return -1;
        }
    }
    return 0;
}
