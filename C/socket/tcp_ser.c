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


int main (int argc,char** argv)
{
    int sockfd,acceptfd,i;
    struct sockaddr_in server,client;
    char buff[256]="";
    socklen_t cli_len;

    cli_len=sizeof(client);

    if(argc!=2){
        printf("Enter ipv4 address at the command line\n");
        return 1;
    }


/*  if ( inet_pton(AF_INET,argv[1],&sever.sin_addr) <= 0){
        printf("Invalid ip\n");
        return 1;
    }
*/

    server.sin_family=AF_INET;
    server.sin_addr.s_addr=INADDR_ANY;
//  server.sin_addr.s_addr=argv[1];
    server.sin_port=6053;

    if ((sockfd=socket(AF_INET,SOCK_STREAM,0))<0){
        perror("Socket\n");
        return 1;
    }

    if (setsockopt(sockfd,SOL_SOCKET,SO_REUSEADDR,&i,sizeof(i)) < 0){
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

    while(1){
        acceptfd = accept(sockfd, (struct sockaddr *)&client, &cli_len);
        if(acceptfd<0) {
            perror("Accept\n");
            return 1;
        }

        bzero(buff, sizeof(buff));
        read(acceptfd, buff, sizeof(buff));

        printf("Read %s\n",buff);
    }

    return 0;
}
