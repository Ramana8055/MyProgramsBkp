#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
int main(int argc, char** argv)
{
    char buf[100]="";
    int x=0;
    if(argc!=2) {
        printf("Parse <xml> file as argument\n");
        return 1;
    }
    sprintf(buf,"xmllint %s 1>/dev/null",argv[1]);
    x=system(buf);
    if(x) {
        printf("Exit status: %d\n",WIFEXITED(x));
        return 1;
    }
    return 0;
}
