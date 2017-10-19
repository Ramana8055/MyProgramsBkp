#include <stdio.h>
#include <string.h>
#include <sys/select.h>
#include <unistd.h>


int main()
{
    int fd;
    int ret;
    char ch;

    fd_set mainfd,rdfd;

    FD_ZERO(&mainfd);
    FD_SET(0, &mainfd);

    while (1) {
        rdfd = mainfd;
        struct timeval tv = {
            .tv_sec = 20,
            .tv_usec = 0
        };
        ret = select(1, &rdfd, NULL,NULL, &tv);
        if (ret < 0) {
            printf("Select\n");
        } else if (ret == 0) {
            printf("Tim: %d\n", FD_ISSET(0,&rdfd));
        } else {
            printf("Event: %d\n", FD_ISSET(0,&rdfd));
            read(0,&ch,1);
            printf("Read : %c\n", ch);
        }
    }
    return 0;
}

