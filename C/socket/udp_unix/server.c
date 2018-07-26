#include "common.h"

int main(int argc, char **argv)
{
    char recv_buf[1024];
    int sock;
    int ret;
    int debug_enable = 0;
    socklen_t len;

    if (argc > 1) {
        debug_enable = 1;
    }

    struct sockaddr_un server;

    sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket :");
        return -1;
    }

    server.sun_family = AF_UNIX;
    strcpy(server.sun_path, SERVER_PATH);

    unlink(SERVER_PATH);

    bind(sock, (struct sockaddr *)&server, sizeof(server));

    if (sock < 0) {
        perror("SOCK\n");
        return -1;
    }

    while (1) {
        ret = recvfrom(sock, recv_buf, 1024, 0, NULL, NULL);
        if (ret < 0) {
            fprintf(stderr, "Recv Failed\n");
            return -1;
        }
        if (debug_enable)
            fprintf(stderr, "Received %d bytes\n", ret);
    }
}
