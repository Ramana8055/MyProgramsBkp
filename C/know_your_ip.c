#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>

int main()
{
	int fd;
	struct ifreq ifr;
	if((fd = socket(AF_INET, SOCK_DGRAM, 0))<0){
		perror("Socket\n");
		return 1;
	}
	ifr.ifr_addr.sa_family = AF_INET;
	strncpy(ifr.ifr_name, "wlan0", IFNAMSIZ-1);
//	strncpy(ifr.ifr_name, "eth0", IFNAMSIZ-1);
	ioctl(fd, SIOCGIFADDR, &ifr);
	close(fd);
	printf("%s\n", inet_ntoa(((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr));
	return 0;
}
