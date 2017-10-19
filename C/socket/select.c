#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<sys/stat.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<net/if.h>
#include<string.h>
#include<fcntl.h>
#include<arpa/inet.h>
#include<sys/ioctl.h>

int main (int argc,char** argv)
{
    int sockfd,acceptfd,i,result;
    struct sockaddr_in server,client;
    char buff[256]="";
    socklen_t cli_len;
    fd_set readfds,testfds;

    cli_len=sizeof(client);

/*  if(argc!=2){
        printf("Enter ipv4 address at the command line\n");
        return 1;
    }


    if ( inet_pton(AF_INET,argv[1],&sever.sin_addr) <= 0){
        printf("Invalid ip\n");
        return 1;
    }
*/
    if ((sockfd=socket(AF_INET,SOCK_STREAM,0))<0){
        perror("Socket\n");
        return 1;
    }

    server.sin_family=AF_INET;
    server.sin_addr.s_addr=htonl(INADDR_ANY);
//  server.sin_addr.s_addr=argv[1];
    server.sin_port=htons(6053);

    if ( setsockopt(sockfd,SOL_SOCKET,SO_REUSEADDR,&i,sizeof(i)) < 0){
        perror("setsockopt\n");
        return 1;
    }

    if ( bind(sockfd, (struct sockaddr *)&server, sizeof(struct sockaddr_in)) < 0 ){
        perror("Bind\n");
        return 1;
    }

    if ( listen(sockfd,5) < 0 ){
        perror("Listen\n");
        return 1;
    }

    FD_ZERO(&readfds);
    FD_SET(sockfd,&readfds);

    while(1){

        char ch;
        int fd;
        int nread;

        testfds=readfds;

        printf("Server waiting\n");
        result = select(FD_SETSIZE, &testfds, (fd_set*)0,
                (fd_set*)0, (struct timeval *)0);


        if(result < 1) {
            perror("Server5\n");
            exit(1);
        }

        for(fd = 0; fd < FD_SETSIZE ; fd++) {
            if(FD_ISSET(fd,&testfds)) {
                if(fd == sockfd) {
                    acceptfd = accept(sockfd, (struct sockaddr *)&client, &cli_len);
                    FD_SET(acceptfd,&readfds);
                    printf("Adding Client on fd %d\n", acceptfd);
                }
                else {
                    ioctl(fd, FIONREAD, &nread);

                    if(nread == 0) {
                        close(fd);
                        FD_CLR(fd, &readfds);
                        printf("Removing client on fd %d\n",fd);
                    }
                    else {
                        read(fd,&ch,1);
                        sleep(5);
                        printf("Serving client on fd %d\n",fd);
                        ch++;
                        write(fd,&ch,1);
                    }
                }
            }
        }

    }

    return 0;
}
