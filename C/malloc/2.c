#include<stdio.h>
#include<stdlib.h>

int main(void)
{
	char *some_memory;
	int size_to_allocate=1024;
	int megs_obtained=0;
	int ks_obtained=0;

	while(1){
		for(ks_obtained=0;ks_obtained<1024;ks_obtained++){
			some_memory=(char*)malloc(size_to_allocate);
			if(some_memory==NULL){
				perror("Out of memory\n");
				exit(1);
			}
			sprintf(some_memory,"Hello World\n");
		}
		megs_obtained++;
		printf("Allocated %d bytes\n",megs_obtained);
	}
	exit(0);
}
