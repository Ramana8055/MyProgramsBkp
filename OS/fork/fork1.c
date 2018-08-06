#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main(void)
{
    pid_t pid;
    int   rc;

    switch(pid = fork()) {
        case -1:
            perror("fork failed");
            exit(1);
        case 0:
            printf("child: my pid is %d\n", getpid());
            printf("child: parents pid %d\n", getppid());
            printf("child: you choose my last wish[0/1]\n");
            scanf("%d", &rc);
            printf("child: I'm dying :-(\n");
            exit(rc);
        default:
            printf("parent: my pid is %d\n", getpid());
            printf("parent: child pid is : %d\n", pid);
            printf("parent: somebody save my child\n");
            wait(&rc);
            printf("parent: my child is dead saying: %d\n", WEXITSTATUS(rc));
            printf("parent: I'm done with this cruel world!! Good bye!!\n");
    }
    return 0;
}
