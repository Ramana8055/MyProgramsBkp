#include<stdio.h>
#include<signal.h>
int main(){
//	signal(SIGTSTP,SIG_DFL);
	signal(SIGTSTP,SIG_IGN);

	while(1);
}
