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
    int              len;

    if ((key = ftok(KEYFILE, KEYID)) == -1) {
        perror("ftok");
        return -1;
    }

    if ((msqid = msgget(key, 0644 | IPC_CREAT)) == -1) {
        perror("msgget");
        return -1;
    }

    printf("Enter the code words ... press ctrl + d when you are done\n");

    buf.m_type = 2; /* Another secret code */

    while (fgets(buf.m_text, sizeof(buf.m_text), stdin) != NULL) {
        len = strlen(buf.m_text);

        /* We are smart and don't need a new line char */
        if (buf.m_text[len - 1] == '\n') {
            buf.m_text[len - 1] = '\0';
        }

        if (msgsnd(msqid, &buf, len + 1 /* why +1 ?*/, 0) == -1) {
            perror("msgsnd");
        }
    }

    if (msgctl(msqid, IPC_RMID, NULL) == -1) {
        perror("msgctl");
        return -1;
    }
    return 0;
}
