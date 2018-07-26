#include "common.h"

int main()
{
    int    ret;
    char   snd_buf[1024];
    int    sock;
    struct sockaddr_un server;

    sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket :");
        return -1;
    }
    server.sun_family = AF_UNIX;
    strcpy(server.sun_path, SERVER_PATH);

    memset(snd_buf, 0, 500);

    while (1) {

        usleep(1000);

        if (sendto(sock, snd_buf, 500, 0,
            (struct sockaddr *)&server, sizeof(server)) == -1) {

            fprintf(stderr, "Recv Failed\n");
            return -1;
        }

    }
}
