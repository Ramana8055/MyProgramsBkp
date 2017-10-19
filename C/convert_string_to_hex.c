#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    int i;
    int len;
    int temp = 0;
    int pay_len;

    char buf1[56];
    char buf2[28];

    char *ptr1 = buf1;
    char *ptr2 = buf2;

    memset(buf1, 0, sizeof(buf1));
    memset(buf2, 0, sizeof(buf2));


    scanf("%s", buf1);

    printf("Read : %s\n", buf1);


    len = strlen(buf1);
    printf("len: %d\n", len);
    if (buf1[len -1] == '\n') {
        buf1[len - 1] = '\0';
        len --;
    }
    printf("len: %d\n", len);

    for (i = 0; i < len/2 ; i++) {
       sscanf(ptr1, "%02x", &temp);
       printf("%02x\n", temp);
       buf2[i] = temp & 0xff;
       ptr1 += 2;
    }
    len = i;
    
    for (i = 0; i < len ; i++) {
        printf("%02x", buf2[i]);
    }
    printf("\n");

}
