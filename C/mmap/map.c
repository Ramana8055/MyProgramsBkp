#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<fcntl.h>
#include<sys/mman.h>

typedef struct {
    int integer;
    char string[24];
} RECORD;

#define NRECORDS 100

int main(void)
{
    RECORD record, *mapped;
    int i,f;
    FILE *fp;

    //Create a file and write 100 lines

    if( (fp = fopen("file.txt","wb+")) == NULL ){
        perror("Open");
        exit(1);
    }

    for( i=0; i<NRECORDS ; i++) {
        record.integer = i;
        sprintf(record.string,"RECORD--%d",i);
        fwrite(&record,sizeof(record),1,fp);
    }
    fclose(fp);


    //Change something:Here change int value at record 43 to 143

    if ((fp = fopen("file.txt","rb+")) == NULL){
        perror("Open\n");
        exit(1);
    }

    fseek(fp,43*sizeof(record),SEEK_SET);

    fread(&record,sizeof(record),1,fp);

    record.integer=143;
    sprintf(record.string,"RECORD--%d",record.integer);

    fseek(fp,43*sizeof(record),SEEK_SET);

    fwrite(&record,sizeof(record),1,fp);

    fclose(fp);

    //Mapping the records

    f = open("file.txt",O_RDWR);

    mapped = (RECORD *)mmap(0,NRECORDS*sizeof(record),PROT_READ|PROT_WRITE,
            MAP_SHARED,f,0);

    //Change to 243
    mapped[43].integer=243;
    sprintf(mapped[43].string,"RECORD--%d",mapped[43].integer);


    msync( (void *)mapped, NRECORDS*sizeof(record),MS_ASYNC);

    //Un map the memory

    munmap( (void *)mapped, NRECORDS*sizeof(record) );

    close(f);

    exit(0);
}
