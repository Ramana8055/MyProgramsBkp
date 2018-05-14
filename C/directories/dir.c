#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>

int main(int argc,char **argv)
{
    struct dirent   *d   = NULL;
    DIR             *dir = NULL;

    if (2 != argc){
        printf("Enter a directory name to list\n");
        return -1;
    }

    dir = opendir(argv[1]);
    if (NULL == dir){
        perror("Open Failed\n");
        return -1;
    }

    while ( NULL != (d = readdir(dir))) {
        printf("%s\n", d->d_name);
    }

    return 0;
}
