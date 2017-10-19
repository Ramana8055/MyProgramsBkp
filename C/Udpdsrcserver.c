#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <time.h>

#define BUF_SIZE 2048
#define WSMP_LEN_START_OFFSET  27
#define WSMP_PSID_START 15
#define WSMP_CHANNEL_BYTE_OFFSET 17
#define WSMP_LEN_BYTE_OFFSET 25

typedef struct infusion_header {
    uint8_t         version;
    uint8_t         type;
    uint32_t        len;
    uint32_t        seconds;
    uint16_t        msecs;
    uint32_t        rseID;
    uint32_t        psid;
    uint32_t        extra;
    uint32_t        extra2;
    uint8_t         extra3;
    uint8_t         payload[0];
} infusion_header_t;

int infusion_enabled;

char* get_timestamp ()
{
  time_t now = time (NULL);
  return asctime (localtime (&now));
}
struct psid_info {
    uint32_t psid;
    int      psidlen;
};
int get_psid_length(uint8_t *psid)
{
    if ((psid[0] & 0xF0) == 0xF0) {
        return -1;
    } else if ((psid[0] & 0xE0) == 0xE0) {
        return 4;
    } else if ((psid[0] & 0xE0) == 0xC0) {
        return 3;
    } else if ((psid[0] & 0xC0) == 0x80) {
        return 2;
    } else if ((psid[0] & 0x80) == 0x00) {
        return 1;
    }
    return -1;
}
void get_psid_value(uint8_t *psid, struct psid_info *psid_info)
{
    uint8_t value[4];
    uint32_t psidlen = get_psid_length(psid);
    memset(value, 0, sizeof(value));
    memcpy (&value[sizeof(value)-psidlen], psid, psidlen);
    psid_info->psid = ntohl(*(uint32_t*)value);
    psid_info->psidlen = psidlen;
}
void parse_psid(unsigned char *buf, struct psid_info *psid_info) {
    uint8_t PSID[4];
    memcpy(PSID, buf, 4);
    get_psid_value(PSID, psid_info);

}
unsigned long unpack_2bytes(unsigned char *buf)
{
    return ((buf[0] << 8) | buf[1]);
}
void parse_infusion_msg(unsigned char *msg)
{
    int i,len = 0;
    struct psid_info psid_info;
    infusion_header_t *infh = (infusion_header_t *)msg;
    printf("--------------------------------------------\n");
    printf("Infusion header version 0x%X\n", infh->version);
    printf("RseId 0x%X\n", htonl(infh->rseID));
    printf("Type %d\n", infh->type);
    parse_psid((unsigned char*)&infh->psid, &psid_info);
    printf("Psid: 0x%X len: %d\n", psid_info.psid, psid_info.psidlen);
    printf("Seconds %d\n", ntohl(infh->seconds));
    printf("Msecs %d\n", ntohs(infh->msecs));
    len = ntohl(infh->len);
    printf("Payload len %d\n", len);
    printf("Payload:\n");
    for (i=0; i < len; i++) {
        printf("%.2X", infh->payload[i]);;
    }
    printf("\n\n");
    printf("--------------------------------------------\n");
    return;
}
void parse_dsrc_msg(unsigned char *msg)
{
    unsigned long channel = 0;
    unsigned long payload_length = 0;
    struct psid_info psid_info;
    int i = 0;
    static uint32_t count = 1;
    printf("--------------------------------------------\n");
    printf("Timestamp: %s",get_timestamp());
    printf("WSMP message count: %u\n", count++); 
    parse_psid(&msg[WSMP_PSID_START], &psid_info);
    printf("psid: 0x%X len: %d\n", psid_info.psid, psid_info.psidlen);
    channel = msg[WSMP_CHANNEL_BYTE_OFFSET + psid_info.psidlen];
    printf("channel: %lu\n", channel);
    payload_length = unpack_2bytes(&msg[WSMP_LEN_BYTE_OFFSET + psid_info.psidlen]);
    printf("payload_length: %lu\n", payload_length);
    printf("payload: \n");
    for (i = 0; i < payload_length; i++) {
        if (i) {
            if ((i % 16) == 0) {
                printf("\n");
            } else if ((i % 8) == 0) {
                printf("  ");
            } else {
                printf(" ");
            }
        }
       printf("%02x", msg[i + WSMP_LEN_START_OFFSET + psid_info.psidlen]);
    }
    printf("\n\n");
    printf("--------------------------------------------\n");
}
void udp_handler(int sock, int addr_type, int delay)
{
    int ret = 0;
    unsigned char buf[BUF_SIZE];
    while (1) {
        ret = recvfrom(sock, buf, BUF_SIZE, 0, NULL, NULL);
        if(ret <= 0) {
            perror("recvfrom ");
            close(sock);
            exit(1);
        }
        if(infusion_enabled) {
            parse_infusion_msg(buf);
        } else {
            parse_dsrc_msg(buf);
        }
        if(delay > 0) {
            sleep(delay);
        }
    }
}
int main(int argc, char **argv)
{
    int sock;
    int port;
    int addr_type;
    struct sockaddr_in serverip;
    struct sockaddr_in6 serverip6;
    int one = 1;
    int delay = 0;
    if (argc != 5) {
        printf("%s port ip wait-time(s) infusion\n", argv[0]);
        return 1;
    }
    delay = atoi(argv[3]);
    port = atoi(argv[1]);
    infusion_enabled = atoi(argv[4]);

    if (inet_pton(AF_INET, argv[2], &serverip.sin_addr) == 0) {
        if (inet_pton(AF_INET6, argv[2], &serverip6.sin6_addr) == 0) {
            printf("invalid ip\n");
            return 1;
        }
        addr_type = AF_INET6;
        serverip6.sin6_family = AF_INET6;
        serverip6.sin6_port = htons(port);
        serverip6.sin6_scope_id = if_nametoindex("eth0");
        serverip6.sin6_addr = in6addr_any;
    } else {
        addr_type = AF_INET;
        serverip.sin_family = AF_INET;
        serverip.sin_port = htons(port);
        serverip.sin_addr.s_addr = INADDR_ANY;
    }
    sock = socket(addr_type, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("can't init socket ");
        return 1;
    }
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) < 0) {
        perror("can't perform setsocketopt ");
        close(sock);
        return 1;
    }
    if (addr_type == AF_INET6) {
        if (bind(sock, (struct sockaddr *)&serverip6, sizeof(struct sockaddr_in6)) < 0) {
            perror("can't bind ");
            close(sock);
            return 1;
        }
    } else {
        if (bind(sock, (struct sockaddr *)&serverip, sizeof(struct sockaddr_in)) < 0) {
            perror("can't bind ");
            close(sock);
            return 1;
        }
    }
    udp_handler(sock, addr_type, delay);
    return 0;
}
