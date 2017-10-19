#include<stdio.h>
int main(){
	int i,j,k;
	printf("Enter a number(1-9)\n");
	scanf("%d",&i);
	for(j=0;j<i;j++){
		for(k=j+1;k<=i;k++)
			printf("%d ",k);
		printf("\n");
	}
	return 0;
}
