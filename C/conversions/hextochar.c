#include<stdio.h>
#include<stdlib.h>
int main(int argv, char **argc)
{
    int c=1;
    if (argv == 1) {
        printf("Enter hex stream follwed by spaces\n");
        return 1;
    }
    argv -= 1;
    while (argv--)
        printf("%c",(char)strtol(argc[c++],NULL,16));
    printf("\n");
    return 0;
}
