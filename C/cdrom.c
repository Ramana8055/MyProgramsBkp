#include <stdio.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <linux/cdrom.h>
#include <errno.h>
#include <unistd.h>

int main()
{
    int fd;

    fd=open("/dev/cdrom",O_RDWR|O_NONBLOCK);
    if(fd<0){
        perror("failed\n");
        return errno;
    }
    while(1)
    {
        ioctl(fd,CDROMEJECT);
        sleep(1);
//      ioctl(fd,CDROMCLOSETRAY);
        sleep(3);
    }
    close(fd);
    return 0;
}

