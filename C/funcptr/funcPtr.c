#include<stdio.h>

int (*ptr2func)(int,int);

int add(int a,int b){
    return a+b;
}

int sub(int a,int b){
    return a-b;
}

int mul(int a,int b){
    return a*b;
}

int div(int a, int b){
    return a/b;
}

int main(void){
    int i,j;
    char c;

    printf("Enter two nums\n");
    scanf("%d %d",&i,&j);

    printf("Enter an operator\n");
    scanf(" %c",&c);

    switch(c){

    case '+': ptr2func=&add;
          printf("Sum is %d\n",ptr2func(i,j));   //Can also be used as (*ptr2func)(i,j)
          break;
    case '-': ptr2func=&sub;
          printf("Diff is %d\n",(*ptr2func)(i,j));
          break;
    case '*': ptr2func=&mul;
          printf("Pro is %d\n",ptr2func(i,j));
          break;
    case '/': ptr2func=&div;
          printf("Div is %d\n",ptr2func(i,j));
          break;
    default: printf("Invalid operator %c\n",c);
         return 1;
    }
    return 0;
}
