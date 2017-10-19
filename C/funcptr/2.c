#include<stdio.h>

typedef int (*ptr2func)(int,int);
ptr2func funcs[4];

/*
* above two lines are equivalent to 
* int (*funcs[4])(int,int);
*/

int add(int a,int b){
	return a+b;
}
int sub(int a,int b){
	return a-b;
}
int mul(int a,int b){
	return a*b;
}
int div(int a,int b){
	return a/b;
}

int main()
{
	int i,j;
	char c;
	printf("Enter two numbers\n");
	scanf("%d %d",&i,&j);

	printf("Enter operator\n");
	scanf(" %c",&c);

	switch(c){
	
	case '+': funcs[0]=&add;
		  //printf("Sum is %d\n",funcs[0](i,j));
		  printf("Sum is %d\n",(*funcs)(i,j));
		  break;

	case '-': funcs[1]=&sub;
		  //printf("Diff is %d\n",funcs[1](i,j));
		  printf("Diff is %d\n",(*(funcs+1))(i,j));
		  break;
	case '*': funcs[2]=&mul;
		  printf("Mul is %d\n",funcs[2](i,j));
		  break;

	case '/': funcs[3]=&div;
		  printf("Div is %d\n",funcs[3](i,j));
		  break;

	default:
		printf("Invalid operator %c\n",c);
		return 1;
	}
	return 0;
}
