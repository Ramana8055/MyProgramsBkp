#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>

struct my_msgbuf {
    long m_type;
    char m_text[200];
};

#define KEYFILE "./common.h"
#define KEYID   'B' /* My secret mission code name */
