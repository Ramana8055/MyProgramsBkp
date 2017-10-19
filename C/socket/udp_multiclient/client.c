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


socket_t
udpc_init(char *ifaddr, int *size)
{
    socket_t sock;
    int family = AF_INET;
    int ret = -1;
    struct sockaddr_in addr;

    if (inet_pton(family, ifaddr, &(addr.sin_addr)) == 0) {
        *size = sizeof(addr);
    }

    sock = socket(family, SOCK_DGRAM, 0);
    if (sock < 0) {
        return ret;
    }
    return sock;
}

int main()
{
    socket_t sock;
    int size;
    int ret;
    char buf[32];

    sock = udpc_init("127.0.0.1", &size);

    while (1) {
        ret = sendto(sock, "hello", 6, 0, 0, 0);
        if (ret < 0) {
            fprintf(stderr, "exit at %d\n", __LINE__);
            return -1;
        }

        memset(buf, 0, 32);

        ret = recvfrom(sock, buf, sizeof(buf), 0, 0, 0);
        if (ret < 0) {
            fprintf(stderr, "exit at %d\n", __LINE__);
            return -1;
        }
        fprintf(stderr, "received %s\n", buf);
    }
}
