#include<stdio.h>
#include<signal.h>
#include<stdlib.h>
#include<fcntl.h>

int main()
{
    int fd, i;

    fd=open("fifo",O_RDONLY,0666);
    if(fd<0)
    {
        perror("open\n");
        exit(1);
    }
    read(fd,(int *)&i,sizeof(i));
    sleep(2);
    while(1)
        kill(i,SIGINT);
    return 0;
}

