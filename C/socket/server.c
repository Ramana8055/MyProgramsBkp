#include <stdio.h>
#include <stdint.h>
#include <strings.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <getopt.h>

void run_tcp_server(int sockfd, struct sockaddr_in6 *server, char *intf)
{
    int  afd;
    int  len;
    char buf[1024];
    int  ret;

    len = sizeof(struct sockaddr_in6);
    listen(sockfd, 1);

    while (1) {
        afd = accept(sockfd, (struct sockaddr *)server, &len);
        if (afd < 0) {
            perror("accept: ");
            return;
        }

        while (1) {
            bzero(buf, sizeof(buf));
            ret = read(afd, buf, sizeof(buf));
            if (ret <= 0) {
                perror("read\n");
                close(afd);
                break;
            }
            printf("Received: %s\n", buf);
        }
    }
}

void run_udp_server(int sockfd, struct sockaddr_in6 *server, char *intf)
{
    int                 ret;
    char                buf[1024];
    struct sockaddr_in6 client;
    while (1) {
        bzero(buf, sizeof(buf));
        ret = recvfrom(sockfd, buf, sizeof(buf), 0, NULL, NULL);
        if (ret <= 0) {
            perror("recvfrom: ");
            return;
        }
        printf("recved: %s\n", buf);
    }
}

void usage()
{
    fprintf(stderr, "Usage:\n"
             "\t-p<port_number> : Any value within 1024-65534; Default: 2001\n"
             "\t-P<protocol>    : 1-TCP 2-UDP;                 Default: TCP\n"
             "\t-i<interface>   : Interface Name;              Default: ath0\n"
             );
}

int main(int argc, char **argv)
{
    int      sockfd;
    int      protocol = 1;
    uint16_t port     = 2001;
    char     *ifname  = "ath0";
    int      opt      = 1;
    int      option   = -1;

    struct sockaddr_in6 server;

    while ((option = getopt(argc, argv, "p:i:P:h")) != -1) {
        switch(option) {
            case 'p':
                port = (uint16_t) atoi(optarg);
                if (port < 1024 || port > 65535) {
                    fprintf(stderr, "Invalid port\n");
                    usage();
                    return -1;
                }
                break;
            case 'P':
                protocol = atoi(optarg);
                if (protocol != 1 && protocol != 2) {
                    fprintf(stderr, "Invalid protocol\n");
                    usage();
                    return -1;
                }
                break;
            case 'i':
                ifname = optarg;
                if (!ifname) {
                    fprintf(stderr, "Invalid ifname\n");
                    usage();
                    return -1;
                }
                break;
            case 'h':
                usage();
                return 0;
                break;
            default:
                usage();
                return -1;
        }
    }

    server.sin6_family      = AF_INET6;
    server.sin6_port        = htons(port);
    /* Required for link-local ipv6 addresses */
    server.sin6_scope_id    = if_nametoindex(ifname);
    server.sin6_addr        = in6addr_any;

    if (protocol == 1) {
        sockfd = socket(AF_INET6, SOCK_STREAM, 0);
    } else {
        sockfd = socket(AF_INET6, SOCK_DGRAM, 0);
    }
    if (sockfd < 0) {
        perror("Socket: ");
        return -1;
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt: ");
        goto out;
    }

    if (bind(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("Bind: ");
        goto out;
    }

    if (protocol == 1) {
        run_tcp_server(sockfd, &server, ifname);
    } else {
        run_udp_server(sockfd, &server, ifname);
    }
out:
    close(sockfd);
    return -1;
}
