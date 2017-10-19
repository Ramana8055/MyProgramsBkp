#include <stdio.h>

struct xy {
    int len;
    char len2;
    int len3;
    char data[500];
    int len4;
};

#define LEN2 (&((struct xy *)0)->len2) //gives length of the structure till len2
#define LEN3 (&((struct xy *)0)->len3) //gives length of the structure till len3
#define LEN4 (&((struct xy *)0)->len4) //gives length of the structure till len4

int main()
{
    printf("%ld\n", (long)LEN2);
    printf("%ld\n", (long)LEN3);
    printf("%ld\n", (long)LEN4);
}
