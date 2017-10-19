#include<stdio.h>
void handler(int signal){
	printf("%d signal is recievd\n",signal);
}
int main(){
	int i;
	for(i=1;i<=31;i++)
		signal(i,handler);
	while(1);
}
