#include "common.h"


int udps_unix_init(char *path, struct sockaddr_un *server_addr)
{
    struct sockaddr_un server;
    int sk;

    sk = socket(AF_UNIX, SOCK_DGRAM, 0);

    if (sk < 0) {
        return -1;
    }

    server.sun_family = AF_UNIX;
    strcpy(server.sun_path, path);
    unlink(path);

    if (bind(sk, (struct sockaddr *)&server, SUN_LEN(&server)) < 0) {
        close(sk);
        return -1;
    }

    *server_addr = server;

    return sk;
}

int main()
{
    char buf[20];
    int sock;
    int ret;
    socklen_t len;

    struct sockaddr_un server;
    struct sockaddr_un client;
    struct sockaddr_un client2;

    client.sun_family = AF_UNIX;
    strcpy(client.sun_path, CLIENT1_SOCK);

    client2.sun_family = AF_UNIX;
    strcpy(client2.sun_path, CLIENT2_SOCK);

    len = sizeof(client);

    sock = udps_unix_init(SERVER_SOCK, &server);

    if (sock < 0) {
        perror("SOCK\n");
        return -1;
    }

    while (1) {
        sleep(1);

        ret = sendto(sock, "Hello1\n", sizeof("Hello1\n"), 0,
                    (struct sockaddr *)&client, len);
        if (ret < 0) {
            fprintf(stderr, "Send Failed\n");
            return -1;
        }
        ret = sendto(sock, "Hello1\n", sizeof("Hello1\n"), 0,
                    (struct sockaddr *)&client2, len);
        if (ret < 0) {
            fprintf(stderr, "Send Failed\n");
            return -1;
        }
    }
}
