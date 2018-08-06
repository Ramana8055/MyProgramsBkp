#include<signal.h>
#include<stdio.h>
#include<stdlib.h>
#include<fcntl.h>
#include<sys/types.h>
void handler(int signum)
{
    printf("signal received\n");
}
int main()
{
    int fd,i;
    signal(SIGINT,handler);

    fd=open("fifo",O_WRONLY,0666);
    if(fd<0)
    {
        perror("open\n");
        exit(1);
    }
    i=getpid();
    write(fd,&i,sizeof(i));
    while(1);
    return 0;
}
