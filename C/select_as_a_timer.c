#include <stdio.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

int main()
{
    int ret;
    struct timeval t;

    while (1) {
        t.tv_sec = 5;
        t.tv_usec = 0;
        ret = select(0, NULL, NULL, NULL, &t);
        if (ret == 0) {
            printf("Timeout\n");
            printf("%lu %lu\n", t.tv_sec, t.tv_usec);
        }
    }
    return 0;
}
