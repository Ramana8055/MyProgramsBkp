#include <sys/shm.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(){
	key_t key=0;
	int shmid;
	char *shmptr;

	key = ftok("/home/savari/C/Shared/1",'m');

	shmid = shmget(key, 256, SHM_R | IPC_CREAT );
	if (shmid == -1 ){
		perror("shmget\n");
		exit(1);
	}

	shmptr = (char *)shmat(shmid,NULL,NULL);
	if (shmptr == (char *)-1){
		perror("shmat\n");
		exit(1);
	}

	printf("You entered : %s\n",shmptr);
	return 0;
}
