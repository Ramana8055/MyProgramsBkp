#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv)
{
    int num, bits;

    unsigned int unsigned_max = 0;
    int positive_max = 0;

    if (argc != 3) {
        printf("%s <num> <num_of_bits[Min:1, Max:32]>\n",argv[0]);
        return -1;
    }

    num  = (int)atoi(argv[1]);
    bits = (int)atoi(argv[2]);

    if (bits <= 0 || bits > 32) {
        printf("Range for bits is [1, 32]\n");
        return -1;
    }

    unsigned_max = pow(2, bits);
    positive_max = pow(2, bits - 1);

    if (bits == 32) {
        printf("0x%X <--> %d\n", num, num);
        return -1;
    }

    if (num >= unsigned_max || num < 0) {
        printf("Out of bound value\n");
        printf("Should be in the limits [0, %d] for %d bits\n", unsigned_max - 1, bits);
        return -1;
    }

    if (num < positive_max)
        printf("0x%X <--> %d\n", num, num);
    else
        printf("0x%X  <--> %d\n", ( (num - unsigned_max) & (unsigned_max - 1) ), (num - unsigned_max) );
    return 0;
}
