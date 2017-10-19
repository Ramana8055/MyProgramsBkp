#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main()
{
    char buf[100] = "";
    FILE *fp = popen("ls -l 2>&1", "r");
    if (!fp) {
        fprintf(stderr, "Failed to open\n");
        return -1;
    }
    fgets(buf, 100, fp);
    fflush(stdout);

    fprintf(stderr, "read %s\n", buf);

    fprintf(stderr, "Exit status %d\n", WEXITSTATUS(pclose(fp)));

    return 0;
}
