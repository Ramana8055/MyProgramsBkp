#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <getopt.h>
#include <ctype.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <linux/if_packet.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>

struct gn_packet {
    struct ether_header eth;
    uint8_t             txbuf[0];
} __attribute__ ((__packed__));

static void usage(char *prog)
{
    fprintf(stderr, "%s:\n"
                    "\t-f <gn_payload_file>\n"
                    "\t-i <Interface>\n"
                    "\t-d To enable debugging\n", prog);
}

static void
print_hex_dump(uint8_t *buf, int buf_len)
{
    int i;
    for (i = 0; i < buf_len; i ++) {
        if (i != 0) {
            if (!(i % 16)) {
                fprintf(stderr, "\n");
            } else if (!(i % 8)) {
                fprintf(stderr, " ");
            }
        }
        fprintf(stderr, "%02x ", buf[i]);
    }
    fprintf(stderr, "\n\n");
}

static int char_to_int(char digit)
{
    if (digit <= '9') {
        return (digit - '0');
    } else if (isupper(digit)) {
        return (digit - 'A' + 10);
    } else {
        return (digit - 'a' + 10);
    }
}

static int convert_to_int(char *str)
{
    return ((char_to_int(str[0]) << 4) +
            (char_to_int(str[1])));
}

static int parse_gn_hex(char *buf, uint8_t *txbuf, int txbuf_len)
{
    char *ptr;
    int  i;
    int  len;
    int  odd = 0;

    len = strlen(buf);

    if (buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
        len --;
    }

    if (len == 0) {
        return len;
    }

    if ((len % 2) != 0)
        odd = 1;

    ptr = buf;

    for (i = 0; i < (len / 2); i ++) {
        if (!isxdigit(*ptr) || !isxdigit(*(ptr + 1))) {
            return -1;
        }
        txbuf[i] = convert_to_int(ptr);
        ptr += 2;
    }

    if (odd) {
        if (isxdigit(*ptr)) {
            txbuf[i] = char_to_int(*ptr);
            i ++;
        } else {
            return -1;
        }
    }
    return i;
}

int main(int argc, char **argv)
{
    int                 sock;
    int                 ret;
    int                 line = 0;
    int                 opt;
    int                 len;
    int                 debug = 0;
    uint8_t             txbuf[2048];
    FILE                *fp;
    char                *ifname = NULL;
    int                 index;
    uint8_t             ifmac[6];
    char                *filename = NULL;
    char                buf[4096];

    struct gn_packet    *gnpacket;
    struct ifreq        ifreq;
    struct sockaddr_ll  raw_addr;

    while ((opt = getopt(argc, argv, "f:i:d")) != -1) {
        switch(opt) {
            case 'f':
                filename = optarg;
                break;
            case 'i':
                ifname = optarg;
                break;
            case 'd':
                debug = 1;
                break;
            default:
                usage(argv[0]);
                goto err3;
        }
    }

    if ((!filename) || (!ifname)) {
        usage(argv[0]);
        goto err3;
    }

    fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Failed to open %s\n", filename);
        goto err3;
    }

    memset(txbuf, 0, sizeof(txbuf));

    gnpacket = (struct gn_packet *)txbuf;

    sock = socket(AF_PACKET, SOCK_RAW, htons(0x8947));
    if (sock < 0) {
        perror("Socket\n");
        goto err2;
    }

    memset(&ifreq, 0, sizeof(ifreq));

    strncpy(ifreq.ifr_name, ifname, IFNAMSIZ - 1);

    ret = ioctl(sock, SIOCGIFINDEX, &ifreq);
    if (ret < 0) {
        perror("ioctl");
        goto err1;
    }

    index = ifreq.ifr_ifindex;

    memset(&ifreq, 0, sizeof(ifreq));

    strncpy(ifreq.ifr_name, ifname, IFNAMSIZ - 1);

    ret = ioctl(sock, SIOCGIFHWADDR, &ifreq);
    if (ret < 0) {
        perror("ioctl");
        goto err1;
    }

    memcpy(ifmac, &ifreq.ifr_hwaddr.sa_data, 6);
    gnpacket->eth.ether_shost[0] = ifmac[0];
    gnpacket->eth.ether_shost[1] = ifmac[1];
    gnpacket->eth.ether_shost[2] = ifmac[2];
    gnpacket->eth.ether_shost[3] = ifmac[3];
    gnpacket->eth.ether_shost[4] = ifmac[4];
    gnpacket->eth.ether_shost[5] = ifmac[5];

    gnpacket->eth.ether_dhost[0] = 0xff;
    gnpacket->eth.ether_dhost[1] = 0xff;
    gnpacket->eth.ether_dhost[2] = 0xff;
    gnpacket->eth.ether_dhost[3] = 0xff;
    gnpacket->eth.ether_dhost[4] = 0xff;
    gnpacket->eth.ether_dhost[5] = 0xff;

    gnpacket->eth.ether_type = htons(0x8947);

    memset(&raw_addr, 0, sizeof(raw_addr));

    raw_addr.sll_ifindex = index;
    raw_addr.sll_halen = IFHWADDRLEN;
    raw_addr.sll_family = AF_PACKET;
    //raw_addr.sll_protocol = htons(0x8947);
    raw_addr.sll_pkttype = PACKET_BROADCAST;
    raw_addr.sll_addr[0] = 0xff;
    raw_addr.sll_addr[1] = 0xff;
    raw_addr.sll_addr[2] = 0xff;
    raw_addr.sll_addr[3] = 0xff;
    raw_addr.sll_addr[4] = 0xff;
    raw_addr.sll_addr[5] = 0xff;

    while (1) {
        memset(buf, 0, sizeof(buf));

        if (fgets(buf, sizeof(buf), fp)) {

            line ++;
            len = parse_gn_hex(buf, gnpacket->txbuf,
                    sizeof(txbuf) - sizeof(struct gn_packet));
            if (len <= 0) {
                fprintf(stderr, "Invalid Payload @ line no : %d\n", line);
                continue;
            }

            if (debug)
                print_hex_dump(gnpacket->txbuf, len);

            ret = sendto(sock, gnpacket, sizeof(struct gn_packet) + len, 0,
                     (struct sockaddr *)&raw_addr, sizeof(struct sockaddr_ll));
            if (ret < 0) {
                perror("Sendto\n");
                goto err1;
            }
        } else {
            fprintf(stderr, "Transmission Compeleted\n");
            goto err1;
        }
    }
err1:
    fclose(fp);
err2:
    close(sock);
err3:
    return 0;
}

