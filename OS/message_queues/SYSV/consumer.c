#include "common.h"

/*
 * Run as many instances you want
 * and have fun
 */
int main(void)
{
    struct my_msgbuf buf;
    int              msqid;
    key_t            key;

    if ((key = ftok(KEYFILE, KEYID)) == -1) {
        perror("ftok");
        return -1;
    }

    if ((msqid = msgget(key, 0664)) == -1) {
        perror("msgget");
        return -1;
    }

    printf("Let's spy on producer\n");

    while (1) {
        if (msgrcv(msqid, &buf, sizeof(buf.m_text), 0 /* why 0 */, 0) == -1) {
            perror("msgrcv");
            return -1;
        }
        printf("Got the code word: %s\n", buf.m_text);
    }

    return 0;
}
