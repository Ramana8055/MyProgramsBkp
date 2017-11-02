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

void usage()
{
    fprintf(stderr, "Usage:\n"
             "\t-p<port_number> : Any value within 1024-65534; Default: 2001\n"
             "\t-P<protocol>    : 1-TCP 2-UDP;                 Default: TCP\n"
             "\t-i<interface>   : Interface Name;              Default: ath0\n"
             "\t-a<ip6addr>     : Ipv6 Address(Mandatory)\n"
             "\t-d              : Print current parameters\n"
             );
}

int main(int argc, char **argv)
{
    int      sockfd;
    int      protocol     = 1;
    uint16_t port         = 2001;
    char     *ifname      = "ath0";
    int      opt          = 1;
    int      option       = -1;
    char     *ip6_addr    = NULL;
    int      ip_prsnt     = 0;
    int      ret          = -1;
    int      debug_enable = 0;

    struct sockaddr_in6 server;

    while ((option = getopt(argc, argv, "p:i:P:a:hd")) != -1) {
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
            case 'a':
                ip6_addr = optarg;

                if (inet_pton(AF_INET6, ip6_addr, &server.sin6_addr) != 1) {
                    fprintf(stderr, "Invalid ip address\n");
                    usage();
                    return -1;
                }
                ip_prsnt = 1;
                break;
            case 'd':
                debug_enable = 1;
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

    if (!ip_prsnt) {
        fprintf(stderr, "parse ip adrress as input\n");
        usage();
        return -1;
    }

    if (debug_enable) {
        fprintf(stderr, "IPv6Addr: %s\n", ip6_addr);
        fprintf(stderr, "Ifname  : %s\n", ifname);
        fprintf(stderr, "Port    : %d\n", port);
        fprintf(stderr, "Proto   : %d\n", protocol);
    }

    server.sin6_family      = AF_INET6;
    server.sin6_port        = htons(port);
    /* Required for link-local ipv6 addresses */
    server.sin6_scope_id    = if_nametoindex(ifname);

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
#if 0
    if (bind(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("Bind: ");
        goto out;
    }
#endif
    if (protocol == 1) {
        ret = connect(sockfd, (struct sockaddr*)&server, sizeof(server));
        if (ret < 0) {
            perror("Connect: ");
            goto out;
        }
        if (debug_enable) {
            printf("Connected\n");
        }
        write(sockfd, "Hello Server", 13);
    } else {
        sendto(sockfd, "Hello Server", 13, 0,
                (struct sockaddr*)&server, sizeof(server));
    }
out:
    close(sockfd);
    return -1;
}
