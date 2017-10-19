#include<unistd.h>
#include<syslog.h>
#include<stdio.h>
#include<stdlib.h>
int main(void)
{
	int fd;

	fd=open("No_such_file","r");
	if(fd<0){
		//Check this in /var/log/syslog
		syslog(LOG_ERR|LOG_USER,"oops no such file %m \n");
		syslog(1,"oops no such file %m \n");
		exit(1);
	}
}
