#include<stdio.h>

struct s1{
	int i;
	char a;
/*	char b;
	char c;
	char d;
	char e;
*/
};

struct __attribute__((__packed__)) s2 {
	int i;
	char a;
/*	char b;
	char c;
	char d;
	char e;
*/
};

int main(void){
	struct s1 S1;
	struct s2 S2;
	printf("%d %d\n",(int)sizeof(S1),(int)sizeof(S2));
	return 0;
}
