#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char** argv)
{
    int num, bits;
    int positive_max;
    int negative_min;
    int unsigned_max;

    if (argc != 3) {
        printf("%s <signed_integers> <num_of_bits[Min 1, Max: 32]>\n", argv[0]);
        return -1;
    }

    num  = (int) atoi(argv[1]);
    bits = (int) atoi(argv[2]);

    if (bits <= 0 || bits > 32) {
        printf("Range for bits is [1,32]\n");
        return -1;
    }

    if (bits == 32) { //Since integer is 32 bit
        printf("Value: %d -->Hex: 0x%X\n", num, num);
        return 0;
    }

    unsigned_max = pow(2, bits);
    negative_min = -pow(2, bits - 1);
    positive_max = pow(2, bits - 1) - 1;

    if (num < negative_min || num > positive_max) {
        printf("Invalid value %d\n", num);
        printf("Range for %d bits is [%d, %d]\n", bits, negative_min, positive_max);
        return -1;
    }

    if (num < 0)
        printf("Value: %d --> Hex: 0x%X\n", num, (unsigned_max + num));
    else
        printf("Value: %d --> Hex: 0x%X\n", num, num);
    return 0;
}

