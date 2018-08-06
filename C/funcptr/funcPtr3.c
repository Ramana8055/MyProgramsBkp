#include<stdio.h>
#include<stdlib.h>

int (*ptr2f)(int,int);

int ( *getOperation(char op) )(int,int);

int add(int a,int b){
    return a+b;
}
int sub(int a,int b){
    return a-b;
}

int ( *getOperation(char op) )(int,int){
    switch(op){

    case '+': return &add;

    case '-': return &sub;

    default:  printf("Invalid operator %c\n",op);
          exit(1);  //Cannot use return 1 since return type is func pointer

    }
}

int main(void){
    int i,j;
    char c;
    printf("Enter two numbers\n");
    scanf("%d %d",&i,&j);

    printf("Enter operator\n");
    scanf(" %c",&c);

    ptr2f = getOperation(c);

    printf("Result is %d\n",ptr2f(i,j));

    return 0;
}
