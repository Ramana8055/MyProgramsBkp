#include"header.h"
void error(char *msg)
{
	perror(msg);
	exit(1);
}
int main()
{
	int fd,sfd,ad,i;
	char buff[1024]="";
	char ch='\0';
	struct sockaddr_in ser,cli;
	socklen_t l=sizeof(cli);
	sfd=socket(AF_INET,SOCK_STREAM,0);
	if(sfd<0)
		error("socket\n");
	ser.sin_addr.s_addr=inet_addr("127.0.0.1");
	ser.sin_port=1234;
	ser.sin_family=AF_INET;
	ad=bind(sfd,(struct sockaddr*)&ser,sizeof(ser));
	if(ad<0)
		error("bind\n");
	ad=listen(sfd,2);
	if(ad<0)
		error("listen\n");
	while(1)
	{
		printf("waiting for a client\n");
		ad=accept(sfd,(struct sockaddr*)&cli,&l);
		if(ad<0)
			error("accept\n");
		printf("connected\n");
		memset(buff,0,sizeof(buff));
		read(ad,buff,sizeof(buff));
		printf("asked for %s\n",buff);
		printf("checking....\n");
		fd=open(buff,O_RDONLY,0666);
		if(fd<0)
		{
			write(ad,"404: File not found\n",20);
			close(ad);
			continue;
		}
		write(ad,"file exists\n",13);
		i=1;
		while(i==1)
		{
			i=read(fd,&ch,1);
			printf("%c",ch);
			if(i==1)
				write(ad,&ch,1);
		}
		printf("\n");
		close(fd);
		close(ad);
	}
	return 0;
}
