#include<stdio.h>
#include<stdlib.h>

int add(int a,int b){
	return a+b;
}

int sub(int a,int b){
	return a-b;
}

typedef (*ptr2f)(int,int);

ptr2f ptr_func;

ptr2f getOperator(char op){

	switch(op){
	
	case '+': return &add;

	case '-': return &sub;

	default:  printf("Invalid operator %c\n",op);
		  exit(1);
	}

}

int main(void){

	int i,j;
	char c;

	printf("Enter two numbers\n");
	scanf("%d %d",&i,&j);

	printf("Enter an operator\n");
	scanf(" %c",&c);

	ptr_func = getOperator(c);

	printf("Result is %d\n",ptr_func(i,j));
	return 0;

}
