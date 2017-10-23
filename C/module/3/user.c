#include<stdio.h>
#include<fcntl.h>
#include<sys/types.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>

int main(){
    int fd;
    char buff[256]="";

    fd=open("/dev/scull2",O_RDWR);
    if (fd<0){
        perror("open failed\n");
        exit(1);
    }

    if(read(fd,"hello Kernel\n",14)<0){
        perror("Read failed\n");
        exit(1);
    }

    if(write(fd,buff,sizeof(buff))<0){
        perror("Write failed\n");
        exit(1);
    }

    printf("Kernel says %s\n",buff);

    return 0;
}
