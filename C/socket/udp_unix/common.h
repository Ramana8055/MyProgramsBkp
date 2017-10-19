#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <unistd.h>

#define CLIENT1_SOCK "/tmp/cli_1.sock"
#define CLIENT2_SOCK "/tmp/cli_2.sock"
#define SERVER_SOCK  "/tmp/server.sock"
