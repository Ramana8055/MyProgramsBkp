#include<stdio.h>
#include<stdint.h>
int main()
{
	uint32_t x,b0,b1,b2,b3,result;
	while(1){
		scanf("%x",&x);

		b0= ( x & 0x000000ff ) << 24;
		b1= ( x & 0x0000ff00 ) << 8;
		b2= ( x & 0x00ff0000 ) >> 8;
		b3= ( x & 0xff000000 ) >> 24;

		result= b0|b1|b2|b3;
		printf("%x\n",result);
	}
	return 0;
}
