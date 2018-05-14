#include <stdio.h>
#include <time.h>
#include <unistd.h>

int main(void){
    time_t now = time(NULL);
    printf("%s",asctime(localtime(&now)));
    return 0;
}
