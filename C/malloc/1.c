#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
int main(void)
{
	char *some_memory;

	while(1){
		some_memory=(char *)malloc(1024*1024);
		if(some_memory==NULL){
			perror("out of memory\n");
			exit(1);
		}
		sprintf(some_memory,"HELLO WORLD\n");
		printf("%s\n",some_memory);
	}
	exit(0);
}
