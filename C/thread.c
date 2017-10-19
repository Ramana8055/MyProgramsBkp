#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<pthread.h>
#include<sys/types.h>
#include<semaphore.h>
int a=0;
sem_t s1;
pthread_mutex_t m1;
void* t1handler(void *data){
    while(1){
        //sem_wait(&s1);
        pthread_mutex_lock(&m1);
        a++;
        printf("incr %d\n",a);
        //sem_post(&s1);
        pthread_mutex_unlock(&m1);
    }
}
void* t2handler(void* data){
    while(1){
        //sem_wait(&s1);
        pthread_mutex_lock(&m1);
        a--;
        printf("decr %d\n",a);
        //sem_post(&s1);
        pthread_mutex_unlock(&m1);
    }
}
int main(){
    pthread_t t1,t2;
    //sem_init(&s1,0,1);
    pthread_mutex_init(&m1,NULL);
    pthread_create(&t1,NULL,t1handler,NULL);
    pthread_create(&t2,NULL,t2handler,NULL);

    pthread_join(t1,NULL);
    pthread_join(t2,NULL);
    return 0;
}
