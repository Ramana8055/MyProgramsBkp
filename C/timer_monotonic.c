#include <stdio.h>
#include <sys/timerfd.h>
#include <stdint.h>
#include <unistd.h>

int main()
{
    int               tfd;
    uint64_t          exp;
    ssize_t           s;
    struct itimerspec its = {0};

    tfd = timerfd_create(CLOCK_MONOTONIC, 0);
    if (tfd == -1) {
        return -1;
    }

    its.it_value.tv_sec  = 0;
    its.it_value.tv_nsec = 100 * 1000000; //100ms
    its.it_interval      = its.it_value;

    if (timerfd_settime(tfd, 0, &its, NULL) < 0) {
        close(tfd);
        return -1;
    }

    while (1) {
        s = read(tfd, &exp, sizeof(exp));
        if (s != sizeof(exp)) {
            fprintf(stderr, "timerfd error\n");
        }

        printf("Time : %ju\n", exp);
    }

    return 0;
}
