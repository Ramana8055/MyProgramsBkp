#include "common.h"

int udpc_unix_init(char *cli_path, char *serv_path, struct sockaddr_un *server_addr)
{
    struct sockaddr_un server, client;
    int sk;

    sk = socket(AF_UNIX, SOCK_DGRAM, 0);

    if (sk < 0) {
        return -1;
    }

    client.sun_family = AF_UNIX;
    strcpy(client.sun_path, cli_path);
    unlink(cli_path);

    if (bind(sk, (void *)&client, SUN_LEN(&client)) < 0) {
        return -1;
    }
    server.sun_family = AF_UNIX;
    strcpy(server.sun_path, serv_path);

    *server_addr = server;

    return sk;
}

int main()
{
    int ret;
    char buf[20];
    int sock;
    socklen_t len;

    struct sockaddr_un server;
    struct sockaddr_un client;

    len = sizeof(client);

    sock = udpc_unix_init(CLIENT1_SOCK, SERVER_SOCK, &server);

    if (sock < 0) {
        perror("SOCK\n");
        return -1;
    }

    while (1) {
        memset(buf, 0, sizeof(buf));
        ret = recvfrom(sock, buf, sizeof(buf), 0,
                (struct sockaddr *)&client, &len);
        if (ret <= 0) {
            fprintf(stderr, "Recv Failed\n");
            return -1;
        }
        printf("Client1 Received: %s\n", buf);
    }
}
