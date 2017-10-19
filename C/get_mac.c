#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <unistd.h>

int main()
{
    int fd;
    struct ifreq ifr;
    char *iface = "wlan0";
    unsigned char *mac;

    fd = socket(AF_INET, SOCK_DGRAM, 0);

    ifr.ifr_addr.sa_family = AF_INET;
    strncpy(ifr.ifr_name , iface , IFNAMSIZ-1);

    ioctl(fd, SIOCGIFHWADDR, &ifr);

    close(fd);

    mac = (unsigned char *)ifr.ifr_hwaddr.sa_data;

    fprintf(stderr, "%02x:%02x:%02x:%02x:%02x:%02x\n" ,
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    return 0;
}
