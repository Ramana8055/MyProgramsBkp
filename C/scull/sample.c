#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "ioctl_base.h"

int main()
{
    int fd;
    char buf[20] = "";

    fd = open("/dev/scull0", O_RDWR);
    if (fd < 0) {
        perror("open\n");
    }

    read(fd, &buf, 20);

    printf("Read from driver: %s\n", buf);

    write(fd, "hello", 6);

    ioctl(fd, SCULL_IO_ONE);
    ioctl(fd, SCULL_IO_TWO);
    ioctl(fd, SCULL_IO_THREE);
    ioctl(fd, SCULL_IO_FOUR);
    ioctl(fd, SCULL_IO_FIVE);

    close(fd);
}
