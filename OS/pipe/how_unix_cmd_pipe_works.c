#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * This is equivalent to "ls | wc -l"
 */

int main(void)
{
    int pfd[2];

    pipe(pfd);

    if (!fork()) {
        close(1); //why..whY wHY WHY? (Comment and check. Now I expect an answer)
        dup(pfd[1]);
        close(pfd[0]);
        execlp("ls", "ls", NULL);
    } else {
        close(0);
        dup(pfd[0]);
        close(pfd[1]);
        execlp("wc", "wc", "-l", NULL);
    }
    return 0;
}
