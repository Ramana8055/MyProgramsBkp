#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>

int main()
{
    int fd;
    int ret;
    char ch;

    fd_set mainfd, rdfd;

    FD_ZERO(&mainfd);

    FD_SET(0,&mainfd);

    struct timeval tv = {
        .tv_sec = 20,
        .tv_usec = 0
    };

    while (1) {
        rdfd = mainfd;

        ret = select(1, &rdfd, NULL, NULL, &tv);

        if (ret < 0) {
            perror("Select\n");
            return -1;
        }

        if (FD_ISSET(0, &rdfd)) {
            printf("SET Ret: %d\n",ret);
            read(0,&ch,1);
            printf("%c\n", ch);
            sleep(1);
        } else {
            printf("Ret :%d\n", ret);
            sleep(1);
        }
    }

}
