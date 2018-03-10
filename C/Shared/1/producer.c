#include <sys/shm.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main()
{
    key_t key=0;
    int   shmid;
    char  *shmptr;
    char  buf[65536];
    int   i;

    memset(buf, 'R', sizeof(buf));

    key = ftok("/home/savari/C/Shared/1",'m');

    shmid = shmget(key, 256, SHM_W | IPC_CREAT );
    if (shmid == -1 ){
        perror("shmget\n");
        return -1;
    }

    shmptr = (char *)shmat(shmid, NULL, 0);
    if (shmptr == (char *)-1){
        perror("shmat\n");
        return -1;
    }

    while (1) {
//        memset(shmptr, 0, 65536);
        if (i > 65535) {
            break;
            i = 1;
        }
        memcpy(shmptr, buf, i - 1);
        usleep(100 * 1000);
        i ++;
    }

    return 0;
}
