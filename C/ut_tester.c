#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <pthread.h>
#include <semaphore.h>
#include <fcntl.h>
#include <UT_SPEC.h>

#define UT_TESTER_SERVER_IP "i:"
#define UT_TESTER_SERVER_PORT "p:"
#define UT_TESTER_LOGFILE_NAME "l:"
#define UT_TESTER_SCRIPT_PATH "f:"

#define UT_TESTER_OPTS              \
                    UT_TESTER_SERVER_IP       \
                    UT_TESTER_SERVER_PORT     \
                    UT_TESTER_LOGFILE_NAME    \
                    UT_TESTER_SCRIPT_PATH

#define UT_TESTER_MAX_PAYLOAD_LEN 4096

#define UT_TESTER_TX_LOG(tx_fp, format, ...) {\
    fprintf(tx_fp, format, __VA_ARGS__);\
    fflush(tx_fp);\
}

#define UT_TESTER_RESP_LOG(resp_fp, format, ...) {\
    fprintf(resp_fp, format, __VA_ARGS__);\
    fflush(resp_fp);\
}

#define UT_TESTER_EVENT_LOG(event_fp, format, ...) {\
    fprintf(event_fp, format, __VA_ARGS__);\
    fflush(event_fp);\
}

static struct timeval tv;
static uint8_t exp_msg_type = 0xFF;

static pthread_t t1;
static pthread_t t2;
//static pthread_mutex_t mutex;
static sem_t s1;
static sem_t s2;

static unsigned long tx_count;
static unsigned long resp_count;
static unsigned long event_count;

#define UT_TESTER_MAX_DENMS 100

static int     new_denm_index;
static int     update_denm_index;
static int     term_denm_index;

struct ut_tester_denm_data {
    int         is_valid;
    uint32_t    station_id;
    uint16_t    sequence_no;
};

static struct ut_tester_denm_data denm_data[UT_TESTER_MAX_DENMS];

struct ut_tester_priv {
    int sock;
    FILE *ts_fp;
    int file_read_complete;
    fd_set allfd;
    int maxfd;
    FILE *event_fp;
    FILE *tx_fp;
    FILE *resp_fp;
    struct sockaddr_in serv_path;
};

static void ut_tester_set_timeout_for_reply()
{
    tv.tv_sec  = 20;
    tv.tv_usec = 0;
}

static void usage(char *progname)
{
    fprintf(stderr, "%s\n"
            "\t-l <log_file> Log file\n"
            "\t-i <ip_addr>  SUT box IP address(Mandatory)\n"
            "\t-f <ts_file>  The TS file to send packets(Mandatory)\n"
            "\t-p <port>     UDP Port. Min: 1, Max: 65535, Default: 65535\n",
            progname);
}

static void
ut_tester_log_indication(struct ut_tester_priv *ut_priv,
                    uint8_t msg_type, uint8_t *buf, int buf_len)
{
    int  i;
    char *ptr;
    char msg[4096];

    memset(msg, 0, sizeof(msg));

    ptr = msg;

    for (i = 0; i < buf_len; i++) {
        sprintf(ptr, "%02x", buf[i]);
        ptr += 2;
    }

    UT_TESTER_EVENT_LOG(ut_priv->event_fp,
                            "%lu,0x%02x,%d,%s\n", ++event_count,
                                                  msg_type, buf_len, msg);
}

static int
ut_tester_setup_client_sock(struct ut_tester_priv *ut_priv,
                    char *ip, int port)
{
    ut_priv->sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (ut_priv->sock < 0) {
        fprintf(stderr, "failed to create udp socket\n");
        return -1;
    }

    ut_priv->serv_path.sin_addr.s_addr = inet_addr(ip);
    ut_priv->serv_path.sin_port = htons(port);
    ut_priv->serv_path.sin_family = AF_INET;

    FD_ZERO(&ut_priv->allfd);

    FD_SET(ut_priv->sock, &ut_priv->allfd);

    if (ut_priv->maxfd < ut_priv->sock)
        ut_priv->maxfd = ut_priv->sock;

    return 0;
}

typedef enum {
    UT_ARG_TYPE_SIGNED_INT,
    UT_ARG_TYPE_UNSIGNED_INT,
    UT_ARG_TYPE_OCTET_STRING,
    UT_ARG_TYPE_DOUBLE,
    UT_ARG_TYPE_STRING,
} UT_ARG_TYPE_t;

static void ut_tester_write_command(struct ut_tester_priv *ut_priv,
                    uint8_t *tx_buf, int tx_msg_len)
{
    int ret;

    ret = sendto(ut_priv->sock, tx_buf, tx_msg_len, 0,
                 (struct sockaddr *)&ut_priv->serv_path,
                 sizeof(ut_priv->serv_path));
    if (ret < 0) {
        fprintf(stderr, "Failed to send request\n");
    }
}

static void
ut_tester_init_log_tx(struct ut_tester_priv *ut_priv,
                    int *hashed_id, uint8_t msg_type)
{
    char log_buf[40];
    int  msg_type_int = 0;

    msg_type_int = msg_type;

    memset(log_buf, 0 , sizeof(log_buf));

    sprintf(log_buf, "%02x%02x%02x%02x%02x%02x%02x%02x",
                     hashed_id[0], hashed_id[1], hashed_id[2], hashed_id[3],
                     hashed_id[4], hashed_id[5], hashed_id[6], hashed_id[7]);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%s\n", ++tx_count,
                                            (msg_type_int & 0xff), log_buf);
}

static void
ut_init_parser_func(char *data, int len, struct ut_tester_priv *ut_priv)
{
    EU_UTInitialize_t init_req;
    int     off = 0;
    int     hashed_id[8];

    memset(&init_req, 0, sizeof(init_req));

    init_req.msg_type = EU_UT_MSG_TYPE_UT_INIT_REQ;

    sscanf(data + off, "%02x", &hashed_id[0]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[1]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[2]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[3]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[4]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[5]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[6]);
    off += 2;

    sscanf(data + off, "%02x", &hashed_id[7]);

    init_req.hashed_id[0] = hashed_id[0] & 0xFF;
    init_req.hashed_id[1] = hashed_id[1] & 0xFF;
    init_req.hashed_id[2] = hashed_id[2] & 0xFF;
    init_req.hashed_id[3] = hashed_id[3] & 0xFF;
    init_req.hashed_id[4] = hashed_id[4] & 0xFF;
    init_req.hashed_id[5] = hashed_id[5] & 0xFF;
    init_req.hashed_id[6] = hashed_id[6] & 0xFF;
    init_req.hashed_id[7] = hashed_id[7] & 0xFF;

#if 0
    printf("%02x %02x %02x %02x %02x %02x %02x %02x\n",
                            init_req.hashed_id[0],
                            init_req.hashed_id[1],
                            init_req.hashed_id[2],
                            init_req.hashed_id[3],
                            init_req.hashed_id[4],
                            init_req.hashed_id[5],
                            init_req.hashed_id[6],
                            init_req.hashed_id[7]);
#endif

    exp_msg_type = EU_UT_MSG_TYPE_UT_INIT_RESP;

    ut_tester_set_timeout_for_reply();

    ut_tester_write_command(ut_priv, (uint8_t *)&init_req, sizeof(init_req));

    ut_tester_init_log_tx(ut_priv, hashed_id, init_req.msg_type);
}

#if 0
static void
ut_delay_parse_func(char *data,
                    int len,
                    struct ut_tester_priv *ut_priv)
{
}
#endif

static void
ut_btpb_gen_parser(char *data, int len, struct ut_tester_priv *ut_priv)
{
    EU_UTBtpTrigger_t btp_trig;
    int dest_port;
    int dest_port_info;

    btp_trig.msg_type = EU_UT_MSG_TYPE_BTP_TRIGGER_B;

    sscanf(data, "%d,%d", &dest_port, &dest_port_info);

    btp_trig.destination_port = htons(dest_port & 0xffff);
    btp_trig.source_port      = htons(dest_port_info & 0xffff);

#if 0
    printf("Dest port %d source %d\n", btp_trig.destination_port,
                                            btp_trig.source_port);
#endif

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_BTP_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&btp_trig, sizeof(btp_trig));

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_BTP_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d,%d\n",
                                    ++tx_count, btp_trig.msg_type,
                                    ntohs(btp_trig.destination_port),
                                    ntohs(btp_trig.source_port));
}

static int
ut_tester_char_to_int(char digit)
{
    if (digit <= '9') {
        return (digit - '0');
    } else if (isupper(digit)) {
        return (digit - 'A' + 10);
    } else {
        return (digit - 'a' + 10);
    }
}

static int
__ut_tester_convert_to_int(char *str)
{
    return ((ut_tester_char_to_int(str[0]) << 4) +
                (ut_tester_char_to_int(str[1])));
}

static int
ut_tester_parse_hex(char *src, uint8_t *data)
{
    char *ptr;
    int i;
    int len;
    char dst[UT_TESTER_MAX_PAYLOAD_LEN];
    int odd = 0;

    len = strlen(src);

    if (len == 0) {
        return len;
    }

    if ((len % 2) != 0)
        odd = 1;

    ptr = src;

    for (i = 0; i < (len / 2); i++) {
        if (!isxdigit(*ptr) || !isxdigit(*(ptr + 1))) {
            return -1;
        }
        dst[i] = __ut_tester_convert_to_int(ptr);
        ptr +=2;
    }

    if (odd) {
        if (isxdigit(*ptr)) {
            dst[i] = ut_tester_char_to_int(*ptr);
            i++;
        } else {
            return -1;
        }
    }

    memcpy(data, dst, i);

    return i;
}


static void
ut_tester_gn_gen_shb_log_tx(struct ut_tester_priv *ut_priv,
                                    EU_UTGnTriggerSHB_t *shb)
{
    int i;
    int payload_len;
    int  msg_type;
    int  traffic_class;

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(buf, 0, sizeof(buf));

    msg_type       = shb->msg_type;
    traffic_class  = shb->traffic_class;
    payload_len    = ntohs(shb->payload_length);

    ptr = buf;

    for (i = 0; i < payload_len; i ++) {
        sprintf(ptr, "%02x", shb->payload[i]);
        ptr += 2;
    }

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d,%d,%s\n", ++tx_count,
                              msg_type, traffic_class, payload_len, buf);
}

static void
ut_gn_gen_shb_parser(char *data,
                     int len,
                     struct ut_tester_priv *ut_priv)
{
    EU_UTGnTriggerSHB_t *shb;
    int     traffic_class;
    int     payload_length;
    uint8_t payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char    str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    shb = (EU_UTGnTriggerSHB_t *)payload;

    sscanf(data, "%d,%s", &traffic_class, str_payload);

    payload_length = ut_tester_parse_hex(str_payload, shb->payload);
    if (payload_length <= 0) {
        fprintf(stderr, "Failed to parse SHB data\n");
        return;
    }

    shb->msg_type       = EU_UT_MSG_TYPE_GN_TRIGGER_SHB;
    shb->traffic_class  = (traffic_class & 0xff);
    shb->payload_length = htons(payload_length & 0xffff);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_GN_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)shb,
            sizeof(EU_UTGnTriggerSHB_t) + payload_length);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_GN_TRIGGER_RESULT);

    ut_tester_gn_gen_shb_log_tx(ut_priv, shb);
}

static void
ut_tester_gn_gen_guc_log_tx(struct ut_tester_priv *ut_priv,
                                EU_UTGnTriggerGUC_t *guc)
{
    int  i;
    int  msg_type;
    int  payload_length;
    int  traffic_class;
    int  lifetime;
    int  gn_addr[8];

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(buf, 0, sizeof(buf));

    msg_type        = guc->msg_type;
    traffic_class   = guc->traffic_class;
    payload_length  = ntohs(guc->payload_length);
    lifetime        = ntohs(guc->lifetime);

    gn_addr[0]      = guc->dest_gn_addr[0];
    gn_addr[1]      = guc->dest_gn_addr[1];
    gn_addr[2]      = guc->dest_gn_addr[2];
    gn_addr[3]      = guc->dest_gn_addr[3];
    gn_addr[4]      = guc->dest_gn_addr[4];
    gn_addr[5]      = guc->dest_gn_addr[5];
    gn_addr[6]      = guc->dest_gn_addr[6];
    gn_addr[7]      = guc->dest_gn_addr[7];

    ptr = buf;

    for (i = 0; i < payload_length; i ++) {
        sprintf(ptr, "%02x", guc->payload[i]);
        ptr += 2;
    }

#define UT_TESTER_GN_ADDR_FMT "%02x:%02x:%02x:%02x:%02x:%02x:%02x:%02x"

#define UT_TESTER_GUC_FMT "%lu,0x%02x,"UT_TESTER_GN_ADDR_FMT",%d,%d,%d,%s\n"

    UT_TESTER_TX_LOG(ut_priv->tx_fp, UT_TESTER_GUC_FMT, ++tx_count,
                            msg_type, gn_addr[0], gn_addr[1], gn_addr[2],
                            gn_addr[3], gn_addr[4], gn_addr[5], gn_addr[6],
                            gn_addr[7], lifetime, traffic_class,
                            payload_length, buf);
#undef UT_TESTER_GUC_FMT
#undef UT_TESTER_GN_ADDR_FMT
}

static void
ut_gn_gen_guc_parser(char *data,
                     int len,
                     struct ut_tester_priv *ut_priv)
{
    EU_UTGnTriggerGUC_t *guc;
    uint8_t             payload[UT_TESTER_MAX_PAYLOAD_LEN];
    int                 payload_length;
    int                 traffic_class;
    int                 lifetime;
    int                 gnaddr[8];
    int                 off = 0;
    char                str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(gnaddr, 0, sizeof(gnaddr));
    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    guc = (EU_UTGnTriggerGUC_t *)payload;

    sscanf(data + off, "%02x", &gnaddr[0]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[1]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[2]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[3]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[4]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[5]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[6]);
    off += 2;

    sscanf(data + off, "%02x", &gnaddr[7]);
    off += 3; //One for comma

    sscanf(data + off, "%d,%d,%s", &lifetime, &traffic_class, str_payload);

    payload_length = ut_tester_parse_hex(str_payload, guc->payload);
    if (payload_length <= 0) {
        fprintf(stderr, "Failed to parse GUC data\n");
        return;
    }

    guc->msg_type        = EU_UT_MSG_TYPE_GN_TRIGGER_GUC;
    guc->dest_gn_addr[0] = gnaddr[0] & 0xff;
    guc->dest_gn_addr[1] = gnaddr[1] & 0xff;
    guc->dest_gn_addr[2] = gnaddr[2] & 0xff;
    guc->dest_gn_addr[3] = gnaddr[3] & 0xff;
    guc->dest_gn_addr[4] = gnaddr[4] & 0xff;
    guc->dest_gn_addr[5] = gnaddr[5] & 0xff;
    guc->dest_gn_addr[6] = gnaddr[6] & 0xff;
    guc->dest_gn_addr[7] = gnaddr[7] & 0xff;

    guc->lifetime        = htons(lifetime);
    guc->traffic_class   = traffic_class & 0xff;
    guc->payload_length  = htons(payload_length);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_GN_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)guc,
            sizeof(EU_UTGnTriggerGUC_t) + payload_length);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_GN_TRIGGER_RESULT);

    ut_tester_gn_gen_guc_log_tx(ut_priv, guc);
}

static void
ut_tester_gn_gen_gbc_log_tx(struct ut_tester_priv *ut_priv,
                            EU_UTGnTriggerGBC_t *gbc)
{
    int i;
    int msg_type;
    int shape;
    int lifetime;
    int traffic_class;
    int lat;
    int lon;
    int dist_a;
    int dist_b;
    int angle;
    int payload_len;

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];


    memset(buf, 0, sizeof(buf));

    msg_type        = gbc->msg_type;
    shape           = gbc->shape;
    lifetime        = ntohs(gbc->lifetime);
    traffic_class   = gbc->traffic_class;
    lat             = ntohl(gbc->latitude);
    lon             = ntohl(gbc->longitude);
    dist_a          = ntohs(gbc->distance_a);
    dist_b          = ntohs(gbc->distance_b);
    angle           = ntohs(gbc->angle);
    payload_len     = ntohs(gbc->payload_length);

    ptr = buf;

    for (i = 0 ; i < payload_len; i ++) {
        sprintf(ptr, "%02x", gbc->payload[i]);
        ptr += 2;
    }

#define UT_TESTER_GBC_FMT "%lu,0x%02x,%d,%d,%d,%d,%d,%hd,%hd,%hd,%d,%s\n"

    UT_TESTER_TX_LOG(ut_priv->tx_fp, UT_TESTER_GBC_FMT,
                                            ++tx_count,
                                            msg_type,
                                            shape,
                                            lifetime,
                                            traffic_class,
                                            lat,
                                            lon,
                                            dist_a,
                                            dist_b,
                                            angle,
                                            payload_len,
                                            buf);
#undef UT_TESTER_GBC_FMT

}

static void
ut_gn_gen_gbc_parser(char *data,
                     int len,
                     struct ut_tester_priv *ut_priv)
{
    EU_UTGnTriggerGBC_t *gbc;
    int     shape;
    int     lifetime;
    int     traffic_class;
    int     latitude;
    int     longitude;
    int     dist_a;
    int     dist_b;
    int     angle;
    int     payload_length;
    uint8_t payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char    str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    gbc = (EU_UTGnTriggerGBC_t *)payload;

    sscanf(data, "%d,%d,%d,%d,%d,%d,%d,%d,%s", &shape,
                                               &lifetime,
                                               &traffic_class,
                                               &latitude,
                                               &longitude,
                                               &dist_a,
                                               &dist_b,
                                               &angle,
                                               str_payload);

    payload_length = ut_tester_parse_hex(str_payload, gbc->payload);
    if (payload_length <= 0) {
        fprintf(stderr, "Failed to parse GBC data\n");
        return;
    }

    gbc->msg_type       = EU_UT_MSG_TYPE_GN_TRIGGER_GBC;
    gbc->shape          = shape & 0xff;
    gbc->lifetime       = htons(lifetime);
    gbc->traffic_class  = traffic_class & 0xff;
    gbc->latitude       = (int32_t)htonl(latitude);
    gbc->longitude      = (int32_t)htonl(longitude);
    gbc->distance_a     = htons(dist_a);
    gbc->distance_b     = htons(dist_b);
    gbc->angle          = htons(angle);
    gbc->payload_length = htons(payload_length);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_GN_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)gbc,
            sizeof(EU_UTGnTriggerGBC_t) + payload_length);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_GN_TRIGGER_RESULT);

    ut_tester_gn_gen_gbc_log_tx(ut_priv, gbc);
}

static void
ut_tester_gn_gen_gac_log_tx(struct ut_tester_priv *ut_priv,
                            EU_UTGnTriggerGAC_t *gac)
{
    int i;
    int msg_type;
    int shape;
    int lifetime;
    int traffic_class;
    int lat;
    int lon;
    int dist_a;
    int dist_b;
    int angle;
    int payload_len;

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(buf, 0, sizeof(buf));

    msg_type        = gac->msg_type;
    shape           = gac->shape;
    lifetime        = ntohs(gac->lifetime);
    traffic_class   = gac->traffic_class;
    lat             = ntohl(gac->latitude);
    lon             = ntohl(gac->longitude);
    dist_a          = ntohs(gac->distance_a);
    dist_b          = ntohs(gac->distance_b);
    angle           = ntohs(gac->angle);
    payload_len     = ntohs(gac->payload_length);

    ptr = buf;

    for (i = 0; i < payload_len; i ++) {
        sprintf(ptr, "%02x", gac->payload[i]);
        ptr += 2;
    }

#define UT_TESTER_GAC_FMT "%lu,0x%02x,%d,%d,%d,%d,%d,%hd,%hd,%hd,%d,%s\n"

    UT_TESTER_TX_LOG(ut_priv->tx_fp, UT_TESTER_GAC_FMT, ++tx_count,
                                                        msg_type,
                                                        shape,
                                                        lifetime,
                                                        traffic_class,
                                                        lat,
                                                        lon,
                                                        (uint16_t)dist_a,
                                                        (uint16_t)dist_b,
                                                        (uint16_t)angle,
                                                        payload_len,
                                                        buf);
#undef UT_TESTER_GAC_FMT
}

static void
ut_gn_gen_gac_parser(char *data,
                     int len,
                     struct ut_tester_priv *ut_priv)
{
    EU_UTGnTriggerGAC_t *gac;

    int     shape;
    int     lifetime;
    int     traffic_class;
    int     latitude;
    int     longitude;
    int     dist_a;
    int     dist_b;
    int     angle;
    int     payload_length;
    uint8_t payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char    str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    gac = (EU_UTGnTriggerGAC_t *)payload;

    sscanf(data, "%d,%d,%d,%d,%d,%d,%d,%d,%s", &shape,
                                               &lifetime,
                                               &traffic_class,
                                               &latitude,
                                               &longitude,
                                               &dist_a,
                                               &dist_b,
                                               &angle,
                                               str_payload);

    payload_length = ut_tester_parse_hex(str_payload, gac->payload);
    if (payload_length <= 0) {
        fprintf(stderr, "Failed to parse GAC data\n");
        return;
    }

    gac->msg_type       = EU_UT_MSG_TYPE_GN_TRIGGER_GAC;
    gac->shape          = shape & 0xff;
    gac->lifetime       = htons(lifetime);
    gac->traffic_class  = traffic_class & 0xff;
    gac->latitude       = (int32_t)htonl(latitude);
    gac->longitude      = (int32_t)htonl(longitude);
    gac->distance_a     = htons(dist_a);
    gac->distance_b     = htons(dist_b);
    gac->angle          = htons(angle);
    gac->payload_length = htons(payload_length);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_GN_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)gac,
            sizeof(EU_UTGnTriggerGAC_t) + payload_length);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_GN_TRIGGER_RESULT);

    ut_tester_gn_gen_gac_log_tx(ut_priv, gac);
}

static void
ut_tester_gn_gen_tsb_log_tx(struct ut_tester_priv *ut_priv,
                            EU_UTGnTriggerTSB_t *tsb)
{
    int i;
    int msg_type;
    int nb_hops;
    int lifetime;
    int traffic_class;
    int payload_len;

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(buf, 0, sizeof(buf));

    msg_type        = tsb->msg_type;
    nb_hops         = tsb->nb_hops;
    lifetime        = htons(tsb->lifetime);
    traffic_class   = tsb->traffic_class;
    payload_len     = htons(tsb->payload_length);

    ptr = buf;

    for (i = 0; i < payload_len; i ++) {
        sprintf(ptr, "%02x", tsb->payload[i]);
        ptr += 2;
    }

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d,%d,%d,%d,%s\n",
                                                    ++tx_count,
                                                    msg_type,
                                                    nb_hops,
                                                    lifetime,
                                                    traffic_class,
                                                    payload_len,
                                                    buf);
}

static void
ut_gn_gen_tsb_parser(char *data,
                     int len,
                     struct ut_tester_priv *ut_priv)
{
    EU_UTGnTriggerTSB_t *tsb;
    int     nb_hops;
    int     lifetime;
    int     traffic_class;
    int     payload_length;
    uint8_t payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char    str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    tsb = (EU_UTGnTriggerTSB_t *)payload;

    sscanf(data, "%d,%d,%d,%s", &nb_hops,
                                &lifetime,
                                &traffic_class,
                                str_payload);

    payload_length = ut_tester_parse_hex(str_payload, tsb->payload);
    if (payload_length <= 0) {
        fprintf(stderr, "Failed to parse TSB data\n");
        return;
    }

    tsb->msg_type       = EU_UT_MSG_TYPE_GN_TRIGGER_TSB;
    tsb->nb_hops        = nb_hops & 0xff;
    tsb->lifetime       = htons(lifetime);
    tsb->traffic_class  = traffic_class & 0xff;
    tsb->payload_length = htons(payload_length);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_GN_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)tsb,
            sizeof(EU_UTGnTriggerTSB_t) + payload_length);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_GN_TRIGGER_RESULT);

    ut_tester_gn_gen_tsb_log_tx(ut_priv, tsb);
}

static void
ut_change_pos_func(char *data,
                   int len,
                   struct ut_tester_priv *ut_priv)
{
    int ret;
    int latitude = 0, longitude = 0, elevation = 0;

    ret = sscanf(data, "%d,%d,%d", &latitude, &longitude, &elevation);
    if (ret != 3) {
        fprintf(stderr, "failed to parse change position command\n");
        return;
    }

    EU_UTChgPosition_t pos;

    pos.msg_type = EU_UT_MSG_TYPE_CHANGE_POS;
    pos.delta_latitude = htonl(latitude);
    pos.delta_longitude = htonl(longitude);
    pos.delta_elevation = elevation & 0xff;

    exp_msg_type = EU_UT_MSG_TYPE_CHANGE_POS_RESP;

    ut_tester_set_timeout_for_reply();

    ut_tester_write_command(ut_priv, (uint8_t *)&pos,
                            sizeof(EU_UTChgPosition_t));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CHANGE_POS_RESP);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d,%d,%d\n",
                                        ++tx_count, (pos.msg_type & 0xff),
                                        ntohl(pos.delta_latitude),
                                        ntohl(pos.delta_longitude),
                                        pos.delta_elevation);
}

static void
ut_cam_curvature_func(char *data,
                      int len,
                      struct ut_tester_priv *ut_priv)
{
    int ret;
    int curvature = 0;

    ret = sscanf(data, "%d", &curvature);
    if (ret != 1) {
        fprintf(stderr, "failed to parse change curvature command\n");
        return;
    }

    EU_UTChangeCurvature_t curvature_cmd;

    curvature_cmd.msg_type = EU_UT_MSG_TYPE_CAM_CHANGE_CURVATURE;
    curvature_cmd.curvature = htons(curvature & 0xffff);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&curvature_cmd,
                            sizeof(curvature_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%hd\n", ++tx_count,
                                (curvature_cmd.msg_type & 0xff),
                                ntohs(curvature_cmd.curvature));
}

static void
ut_cam_speed_func(char *data,
                  int len,
                  struct ut_tester_priv *ut_priv)
{
    int ret;
    int speed = 0;

    ret = sscanf(data, "%d", &speed);
    if (ret != 1) {
        fprintf(stderr, "failed to parse change speed command\n");
        return;
    }

    EU_UTChangeSpeed_t speed_cmd;

    speed_cmd.msg_type = EU_UT_MSG_TYPE_CAM_CHANGE_SPEED;
    speed_cmd.speed = htons(speed);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&speed_cmd,
                            sizeof(speed_cmd));

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%hd\n", ++tx_count,
                                        (speed_cmd.msg_type & 0xff),
                                        ntohs(speed_cmd.speed));
}

static void
ut_cam_set_accel_ctrl_status_func(char *data,
                                  int len,
                                  struct ut_tester_priv *ut_priv)
{
    int ret;
    int accel_ctrl_status = 0;

    ret = sscanf(data, "%x", &accel_ctrl_status);
    if (ret != 1) {
        fprintf(stderr, "failed to parse set accel control status command\n");
        return;
    }

    EU_UTSetAccelerationControlStatus_t accel_status_cmd;

    accel_status_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_ACCEL_CTRL_STATUS;
    accel_status_cmd.acceleration_ctrl_status = accel_ctrl_status;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&accel_status_cmd,
                            sizeof(accel_status_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                        (accel_status_cmd.msg_type & 0xff),
                        (accel_status_cmd.acceleration_ctrl_status & 0xff));
}

static void
ut_cam_set_exterior_lights_func(char *data,
                                int len,
                                struct ut_tester_priv *ut_priv)
{
    int ret;
    int exterior_lights_status = 0;

    ret = sscanf(data, "%x", &exterior_lights_status);
    if (ret != 1) {
        fprintf(stderr, "failed to parse set exterior lights command\n");
        return;
    }

    EU_UTSetExteriorLightsStatus_t exterior_lt_cmd;

    exterior_lt_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_EXTERIOR_LIGHTS_STATUS;
    exterior_lt_cmd.exterior_light_status = exterior_lights_status;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&exterior_lt_cmd,
                            sizeof(exterior_lt_cmd));

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                            (exterior_lt_cmd.msg_type & 0xff),
                            (exterior_lt_cmd.exterior_light_status & 0xff));
}

static void
ut_cam_change_heading(char *data,
                      int len,
                      struct ut_tester_priv *ut_priv)
{
    int ret;
    int heading;

    ret = sscanf(data, "%d", &heading);
    if (ret != 1) {
        fprintf(stderr, "failed to parse change heading\n");
        return;
    }

    EU_UTChangeHeading_t heading_cmd;

    heading_cmd.msg_type = EU_UT_MSG_TYPE_CAM_CHANGE_HEADING;
    heading_cmd.heading_offset = htons(heading);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&heading_cmd,
                            sizeof(heading_cmd));

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                (heading_cmd.msg_type & 0xff),
                                ntohs(heading_cmd.heading_offset));
}

static void
ut_cam_set_driving_direction(char *data,
                             int len,
                             struct ut_tester_priv *ut_priv)
{
    int ret;
    int drive_dir;

    ret = sscanf(data, "%d", &drive_dir);
    if (ret != 1) {
        fprintf(stderr, "failed to parse set drive direction\n");
        return;
    }

    EU_UTSetDriveDirection_t drivedir_cmd;

    drivedir_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_DRIVE_DIRECTION;
    drivedir_cmd.drive_direction = drive_dir;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&drivedir_cmd,
                            sizeof(drivedir_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                    (drivedir_cmd.msg_type & 0xff),
                                    (drivedir_cmd.drive_direction & 0xff));
}

static void
ut_cam_change_yawrate(char *data,
                      int len,
                      struct ut_tester_priv *ut_priv)
{
    int ret;
    int yawrate_delta;

    ret = sscanf(data, "%d", &yawrate_delta);
    if (ret != 1) {
        fprintf(stderr, "failed to parse yawrate\n");
        return;
    }

    EU_UTChangeYawRate_t yawrate_cmd;

    yawrate_cmd.msg_type = EU_UT_MSG_TYPE_CAM_CHANGE_YAWRATE;
    yawrate_cmd.yawrate_offset = htons(yawrate_delta);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&yawrate_cmd,
                            sizeof(yawrate_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%hd\n", ++tx_count,
                                (yawrate_cmd.msg_type & 0xff),
                                ntohs(yawrate_cmd.yawrate_offset));
}

static void
ut_cam_set_station_type(char *data,
                        int len,
                        struct ut_tester_priv *ut_priv)
{
    int ret;
    int station_type = 0;

    ret = sscanf(data, "%d", &station_type);
    if (ret != 1) {
        fprintf(stderr, "failed to parse set station type\n");
        return;
    }

    EU_UTSetStationType_t stationtype_cmd;

    stationtype_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_STATIONTYPE;
    stationtype_cmd.station_type = station_type;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&stationtype_cmd,
                            sizeof(stationtype_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                    (stationtype_cmd.msg_type & 0xff),
                                    (stationtype_cmd.station_type & 0xff));
}

static void
ut_cam_set_vehiclerole(char *data,
                       int len,
                       struct ut_tester_priv *ut_priv)
{
    int ret;
    int vehicle_role = 0;

    ret = sscanf(data, "%d", &vehicle_role);
    if (ret != 1) {
        fprintf(stderr, "failed to parse set vehicle role\n");
        return;
    }

    EU_UTSetVehicleRole_t vehicle_role_cmd;

    vehicle_role_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_VEHICLEROLE;
    vehicle_role_cmd.vehicle_role = vehicle_role;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&vehicle_role_cmd,
                            sizeof(vehicle_role_cmd));

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                    (vehicle_role_cmd.msg_type & 0xff),
                                    (vehicle_role_cmd.vehicle_role & 0xff));
}

static void
ut_cam_set_embarkation_status(char *data,
                              int len,
                              struct ut_tester_priv *ut_priv)
{
    int ret;
    int embarkation_status = 0;

    ret = sscanf(data, "%d", &embarkation_status);
    if (ret != 1) {
        fprintf(stderr, "failed to set embarkation status\n");
        return;
    }

    EU_UTSetEmbarkationStatus_t embarkation_status_cmd;

    embarkation_status_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_EMBARKATIONSTATUS;
    embarkation_status_cmd.embarkation_status = embarkation_status;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&embarkation_status_cmd,
                            sizeof(embarkation_status_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                        (embarkation_status_cmd.msg_type & 0xff),
                        (embarkation_status_cmd.embarkation_status & 0xff));
}

static void
ut_tester_cam_set_pt_activation_log_tx(struct ut_tester_priv *ut_priv,
                                       EU_UTSetPtActivation_t *pt_activation)
{
    int i;
    int msg_type;
    int pt_act_type;
    int pt_act_data_len;

    char *ptr;
    char buf[40];

    memset(buf, 0, sizeof(buf));

    msg_type        = pt_activation->msg_type;
    pt_act_type     = pt_activation->pt_activation_type;
    pt_act_data_len = pt_activation->pt_activation_data_length;

    ptr = buf;

    for (i = 0; i < pt_act_data_len; i ++) {
        sprintf(ptr, "%02x", pt_activation->pt_activation_data[i]);
        ptr += 2;
    }

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%2x,%d,%d,%s\n",
                                        ++tx_count,
                                        msg_type,
                                        pt_act_type,
                                        pt_act_data_len,
                                        buf);
}

static void
ut_cam_set_pt_activation(char *data,
                         int len,
                         struct ut_tester_priv *ut_priv)
{
    int ret;
    int pt_activation_type = 0;
    char pt_activation_data[40];
    int pt_activation_datalen = 0;

    char buf[100];

    memset(pt_activation_data, 0, sizeof(pt_activation_data));

    ret = sscanf(data, "%d,%s", &pt_activation_type, pt_activation_data);
    if (ret != 2) {
        fprintf(stderr, "failed to parse pt activation info\n");
        return;
    }

    EU_UTSetPtActivation_t *pt_activation_cmd;

    memset(buf, 0, sizeof(buf));

    pt_activation_cmd = (EU_UTSetPtActivation_t *)buf;

    pt_activation_cmd->msg_type = EU_UT_MSG_TYPE_CAM_SET_PTACTIVATION;
    pt_activation_cmd->pt_activation_type = pt_activation_type;

    pt_activation_datalen = ut_tester_parse_hex(pt_activation_data,
                                                pt_activation_cmd->pt_activation_data);
    if (pt_activation_datalen <= 0) {
        fprintf(stderr, "failed to parse pt activation data\n");
        return;
    }

    pt_activation_cmd->pt_activation_data_length = (pt_activation_datalen & 0xff);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)pt_activation_cmd,
                        sizeof(EU_UTSetPtActivation_t) + pt_activation_datalen);

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    ut_tester_cam_set_pt_activation_log_tx(ut_priv, pt_activation_cmd);
}

static void
ut_cam_set_dangerous_goods(char *data,
                           int len,
                           struct ut_tester_priv *ut_priv)
{
    int ret;
    int dangerous_goods_val = 0;

    ret = sscanf(data, "%d", &dangerous_goods_val);
    if (ret != 1) {
        fprintf(stderr, "failed to parse dangerous goods\n");
        return;
    }

    EU_UTSetDangerousGoods_t dangerous_goods_cmd;

    dangerous_goods_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_DANGEROUSGOODS;
    dangerous_goods_cmd.dangerous_good = dangerous_goods_val;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&dangerous_goods_cmd,
                            sizeof(dangerous_goods_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                    (dangerous_goods_cmd.msg_type & 0xff),
                                    (dangerous_goods_cmd.dangerous_good & 0xff));
}

static void
ut_cam_set_lightbar_siren_func(char *data,
                               int len,
                               struct ut_tester_priv *ut_priv)
{
    int ret;
    int lightbar_siren = 0;

    ret = sscanf(data, "%x", &lightbar_siren);
    if (ret != 1) {
        fprintf(stderr, "failed to parse lightbar siren\n");
        return;
    }

    EU_UTSetLightBarSiren_t lbsiren_cmd;

    lbsiren_cmd.msg_type = EU_UT_MSG_TYPE_CAM_SET_LIGHTBARSIREN;
    lbsiren_cmd.lightbar_siren = lightbar_siren;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&lbsiren_cmd,
                            sizeof(lbsiren_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                            (lbsiren_cmd.msg_type & 0xff),
                            (lbsiren_cmd.lightbar_siren & 0xff));
}

static void
ut_tester_denm_trigger_log_tx(struct ut_tester_priv *ut_priv,
                              EU_UTDENMTrigger_t *denm_trigger)
{
    int i;
    int msg_type;
    int trigger_mask;
    int det_time[6];
    int val_dur[3];
    int rep_dur[3];
    int info_qual;
    int cause;
    int sub_cause;
    int rel_dist;
    int rel_traf_dir;
    int tx_intvl;
    int rep_intvl;
    int alacarte_length;

    char *ptr;
    char buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(buf, 0, sizeof(buf));

    msg_type        = denm_trigger->msg_type;
    trigger_mask    = denm_trigger->trigger_mask;

    det_time[0]     = denm_trigger->detection_time[0];
    det_time[1]     = denm_trigger->detection_time[1];
    det_time[2]     = denm_trigger->detection_time[2];
    det_time[3]     = denm_trigger->detection_time[3];
    det_time[4]     = denm_trigger->detection_time[4];
    det_time[5]     = denm_trigger->detection_time[5];

    val_dur[0]      = denm_trigger->validity_duration[0];
    val_dur[1]      = denm_trigger->validity_duration[1];
    val_dur[2]      = denm_trigger->validity_duration[2];

    rep_dur[0]      = denm_trigger->repetion_duration[0];
    rep_dur[1]      = denm_trigger->repetion_duration[1];
    rep_dur[2]      = denm_trigger->repetion_duration[2];

    info_qual       = denm_trigger->information_quality;
    cause           = denm_trigger->cause;
    sub_cause       = denm_trigger->subcause;
    rel_dist        = denm_trigger->relevance_distance;
    rel_traf_dir    = denm_trigger->relevance_traffic_direction;

    tx_intvl        = ntohs(denm_trigger->transmission_interval);
    rep_intvl       = ntohs(denm_trigger->repetition_interval);
    alacarte_length = denm_trigger->alacarte_length;

    ptr = buf;

    for (i = 0; i < alacarte_length; i ++) {
        sprintf(ptr, "%02x", denm_trigger->alacarte_container[i]);
        ptr += 2;
    }

#define UT_TESTER_DET_TIME_FMT "%02x%02x%02x%02x%02x%02x"

#define UT_TESTER_VAL_DUR_FMT  "%02x%02x%02x"

#define UT_TESTER_REP_DUR_FMT  "%02x%02x%02x"

#define UT_TESTER_DENM_TRIG_FMT "%lu,0x%02x,0x%02x," \
                                UT_TESTER_DET_TIME_FMT"," \
                                UT_TESTER_VAL_DUR_FMT"," \
                                UT_TESTER_REP_DUR_FMT \
                                ",%d,%d,%d,%d,%d,%d,%d,%d,%s\n"

    UT_TESTER_TX_LOG(ut_priv->tx_fp, UT_TESTER_DENM_TRIG_FMT, ++tx_count,
                                                        msg_type,
                                                        trigger_mask,
                                                        det_time[0],
                                                        det_time[1],
                                                        det_time[2],
                                                        det_time[3],
                                                        det_time[4],
                                                        det_time[5],
                                                        val_dur[0],
                                                        val_dur[1],
                                                        val_dur[2],
                                                        rep_dur[0],
                                                        rep_dur[1],
                                                        rep_dur[2],
                                                        info_qual,
                                                        cause,
                                                        sub_cause,
                                                        rel_dist,
                                                        rel_traf_dir,
                                                        tx_intvl,
                                                        rep_intvl,
                                                        alacarte_length,
                                                        buf);
#undef UT_TESTER_DENM_TRIG_FMT
#undef UT_TESTER_REP_DUR_FMT
#undef UT_TESTER_VAL_DUR_FMT
#undef UT_TESTER_DET_TIME_FMT

}

static void
ut_denm_trigger_parser(char *data,
                       int len,
                       struct ut_tester_priv *ut_priv)
{
    EU_UTDENMTrigger_t *denm_trigger;

    int     trigger_mask;
    int     det_time[6];
    int     val_dur[3];
    int     rep_dur[3];
    int     info_qual;
    int     cause;
    int     sub_cause;
    int     rel_dist;
    int     rel_traf_dir;
    int     tx_intvl;
    int     rep_intvl;
    int     alacarte_length;
    uint8_t payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char    str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    int     ret;
    int     off = 0;

    memset(det_time, 0, sizeof(det_time));
    memset(val_dur, 0, sizeof(val_dur));
    memset(rep_dur, 0, sizeof(rep_dur));
    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(str_payload));

    info_qual = 0;
    cause = 0;
    sub_cause = 0;
    rel_dist = 0;
    rel_traf_dir = 0;
    tx_intvl = 0;
    rep_intvl = 0;
    alacarte_length = 0;

    denm_trigger = (EU_UTDENMTrigger_t *)payload;

    sscanf(data + off, "%02d", &new_denm_index);
    off += 3;

    sscanf(data + off, "%02x", &trigger_mask);
    off += 3; //One for comma

    sscanf(data + off, "%02x", &det_time[0]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[1]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[2]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[3]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[4]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[5]);
    off += 3;

    sscanf(data + off, "%02x", &val_dur[0]);
    off += 2;

    sscanf(data + off, "%02x", &val_dur[1]);
    off += 2;

    sscanf(data + off, "%02x", &val_dur[2]);
    off += 3;

    sscanf(data + off, "%02x", &rep_dur[0]);
    off += 2;

    sscanf(data + off, "%02x", &rep_dur[1]);
    off += 2;

    sscanf(data + off, "%02x", &rep_dur[2]);
    off += 3;

    ret = sscanf(data + off, "%d,%d,%d,%d,%d,%d,%d,%s", &info_qual,
                                                &cause,
                                                &sub_cause,
                                                &rel_dist,
                                                &rel_traf_dir,
                                                &tx_intvl,
                                                &rep_intvl,
                                                str_payload);
    if (ret < 7) {
        fprintf(stderr, "failed to parse information quality,"
                                " cause and subcause\n");
        return;
    }

    alacarte_length = ut_tester_parse_hex(str_payload,
                            denm_trigger->alacarte_container);

    if (alacarte_length < 0) { //Length zero means no alacarte
        fprintf(stderr, "Failed to Parse DENM Trigger data\n");
        return;
    }

    if (new_denm_index < 0 || new_denm_index >= UT_TESTER_MAX_DENMS) {
        fprintf(stderr, "Invalid index for New DENM %d [0, %d]\n",
                                                        new_denm_index,
                                                        UT_TESTER_MAX_DENMS - 1);
        return;
    }

    if (denm_data[new_denm_index].is_valid) {
        fprintf(stderr, "Index not empty for New DENM\n");
        return;
    }


    denm_trigger->msg_type              = EU_UT_MSG_TYPE_DENM_UT_DENM_TRIGGER;
    denm_trigger->trigger_mask          = trigger_mask & 0xff;

    denm_trigger->detection_time[0]     = det_time[0] & 0xff;
    denm_trigger->detection_time[1]     = det_time[1] & 0xff;
    denm_trigger->detection_time[2]     = det_time[2] & 0xff;
    denm_trigger->detection_time[3]     = det_time[3] & 0xff;
    denm_trigger->detection_time[4]     = det_time[4] & 0xff;
    denm_trigger->detection_time[5]     = det_time[5] & 0xff;

    denm_trigger->validity_duration[0]  = val_dur[0] & 0xff;
    denm_trigger->validity_duration[1]  = val_dur[1] & 0xff;
    denm_trigger->validity_duration[2]  = val_dur[2] & 0xff;

    denm_trigger->repetion_duration[0]  = rep_dur[0] & 0xff;
    denm_trigger->repetion_duration[1]  = rep_dur[1] & 0xff;
    denm_trigger->repetion_duration[2]  = rep_dur[2] & 0xff;

    denm_trigger->information_quality   = info_qual & 0xff;
    denm_trigger->cause                 = cause & 0xff;
    denm_trigger->subcause              = sub_cause & 0xff;
    denm_trigger->relevance_distance    = rel_dist & 0xff;
    denm_trigger->relevance_traffic_direction = rel_traf_dir & 0xff;

    denm_trigger->transmission_interval = htons(tx_intvl);
    denm_trigger->repetition_interval   = htons(rep_intvl);

    denm_trigger->alacarte_length       = alacarte_length & 0xff;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_DENM_UT_DENM_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)denm_trigger,
                            sizeof(EU_UTDENMTrigger_t) + alacarte_length);

    ut_tester_denm_trigger_log_tx(ut_priv, denm_trigger);

//    ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_DENM_UT_DENM_TRIGGER_RESULT);
}

static void
ut_tester_denm_update_log_tx(struct ut_tester_priv *ut_priv,
                            EU_UTDENMUpdateDENMEvent_t *denm_update)
{
    int         i;
    int         msg_type = 0;
    int         trigger_mask = 0;
    uint32_t    station_id = 0;
    int         sequence_no = 0;
    int         det_time[6];
    int         val_dur[3];
    int         info_qual = 0;
    int         cause = 0;
    int         sub_cause = 0;
    int         rel_dist = 0;
    int         rel_traf_dir = 0;
    int         tx_intvl = 0;
    int         rep_intvl = 0;
    int         alacarte_length = 0;

    char        *ptr;
    char        buf[UT_TESTER_MAX_PAYLOAD_LEN];

    memset(det_time, 0, sizeof(det_time));
    memset(val_dur, 0, sizeof(val_dur));
    memset(buf, 0, sizeof(buf));

    msg_type            = denm_update->msg_type;
    trigger_mask        = denm_update->trigger_mask;

    station_id          = ntohl(denm_update->station_id);
    sequence_no         = ntohs(denm_update->sequence_no);

    det_time[0]         = denm_update->detection_time[0];
    det_time[1]         = denm_update->detection_time[1];
    det_time[2]         = denm_update->detection_time[2];
    det_time[3]         = denm_update->detection_time[3];
    det_time[4]         = denm_update->detection_time[4];
    det_time[5]         = denm_update->detection_time[5];

    val_dur[0]          = denm_update->validity_duration[0];
    val_dur[1]          = denm_update->validity_duration[1];
    val_dur[2]          = denm_update->validity_duration[2];

    info_qual           = denm_update->information_quality;
    cause               = denm_update->cause;
    sub_cause           = denm_update->subcause;
    rel_dist            = denm_update->relevance_distance;
    rel_traf_dir        = denm_update->relevance_traffic_direction;

    tx_intvl            = ntohs(denm_update->transmission_interval);
    rep_intvl           = ntohs(denm_update->repetition_interval);

    alacarte_length     = denm_update->alacarte_length;

    ptr = buf;

    for (i = 0; i < alacarte_length; i ++) {
        sprintf(ptr, "%02x", denm_update->alacarte_container[i]);
        ptr += 2;
    }

#define UT_TESTER_DET_TIME_FMT "%02x%02x%02x%02x%02x%02x"
#define UT_TESTER_VAL_DUR_FMT  "%02x%02x%02x"

#define UT_TESTER_DENM_UPDATE_FMT "%lu,0x%02x,0x%02x,%u,%d," \
                                  UT_TESTER_DET_TIME_FMT "," \
                                  UT_TESTER_VAL_DUR_FMT "," \
                                  "%d,%d,%d,%d,%d,%d,%d,%d,%s\n"

    UT_TESTER_TX_LOG(ut_priv->tx_fp, UT_TESTER_DENM_UPDATE_FMT, ++tx_count,
                                            msg_type,
                                            trigger_mask,
                                            station_id,
                                            sequence_no,
                                            det_time[0],
                                            det_time[1],
                                            det_time[2],
                                            det_time[3],
                                            det_time[4],
                                            det_time[5],
                                            val_dur[0],
                                            val_dur[1],
                                            val_dur[2],
                                            info_qual,
                                            cause,
                                            sub_cause,
                                            rel_dist,
                                            rel_traf_dir,
                                            tx_intvl,
                                            rep_intvl,
                                            alacarte_length,
                                            buf);
#undef UT_TESTER_DENM_UPDATE_FMT
#undef UT_TESTER_VAL_DUR_FMT
#undef UT_TESTER_DET_TIME_FMT
}

static void
ut_denm_update_parser(char *data,
                      int len,
                      struct ut_tester_priv *ut_priv)
{
    EU_UTDENMUpdateDENMEvent_t *denm_update;

    int         ret = -1;

    int         trigger_mask = 0;
//    uint32_t    station_id   = 0;
//    int         sequence_no  = 0;
    int         det_time[6];
    int         val_dur[3];
    int         info_qual = 0;
    int         cause = 0;
    int         sub_cause = 0;
    int         rel_dist = 0;
    int         rel_traf_dir = 0;
    int         tx_intvl = 0;
    int         rep_intvl = 0;
    int         alacarte_length = 0;
    uint8_t     payload[UT_TESTER_MAX_PAYLOAD_LEN];
    char        str_payload[UT_TESTER_MAX_PAYLOAD_LEN];

    int         off = 0;

    memset(det_time, 0, sizeof(det_time));
    memset(val_dur, 0, sizeof(val_dur));
    memset(payload, 0, sizeof(payload));
    memset(str_payload, 0, sizeof(payload));

    denm_update = (EU_UTDENMUpdateDENMEvent_t *)payload;

    sscanf(data + off, "%02d", &update_denm_index);
    off += 3;

    sscanf(data + off, "%02x", &trigger_mask);
    off += 3;
#if 0
    sscanf(data + off, "%u", &station_id);
    off += 9;

    sscanf(data + off, "%d", &sequence_no);
    off += 5;
#endif
    sscanf(data + off, "%02x", &det_time[0]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[1]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[2]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[3]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[4]);
    off += 2;

    sscanf(data + off, "%02x", &det_time[5]);
    off += 3;

    sscanf(data + off, "%02x", &val_dur[0]);
    off += 2;

    sscanf(data + off, "%02x", &val_dur[1]);
    off += 2;

    sscanf(data + off, "%02x", &val_dur[2]);
    off += 3;

    ret = sscanf(data + off, "%d,%d,%d,%d,%d,%d,%d,%s", &info_qual,
                                                &cause,
                                                &sub_cause,
                                                &rel_dist,
                                                &rel_traf_dir,
                                                &tx_intvl,
                                                &rep_intvl,
                                                str_payload);

    if (ret < 7) {
        fprintf(stderr, "Failed to parse DENM Update event\n");
        return;
    }

    if (update_denm_index < 0 || update_denm_index >= UT_TESTER_MAX_DENMS) {
        fprintf(stderr, "Invalid index for Update DENM %d [0, %d]\n",
                                                            update_denm_index,
                                                            UT_TESTER_MAX_DENMS - 1);
        return;
    }

    if (!denm_data[update_denm_index].is_valid) {
        fprintf(stderr,
                "No valid DENM present at index %d\n", update_denm_index);
        return;
    }

    alacarte_length = ut_tester_parse_hex(str_payload,
                        denm_update->alacarte_container);

    if (alacarte_length < 0) {
        fprintf(stderr, "Failed to parse DENM Update event\n");
        return;
    }

    denm_update->msg_type               = EU_UT_MSG_TYPE_DENM_UT_DENM_UPDATE_DENM;
    denm_update->trigger_mask           = trigger_mask & 0xff;

#if 0
    denm_update->station_id             = htonl(station_id);
    denm_update->sequence_no            = htons(sequence_no);
#endif

    denm_update->station_id             = htonl(denm_data[update_denm_index].station_id);
    denm_update->sequence_no            = htons(denm_data[update_denm_index].sequence_no);

    denm_update->detection_time[0]      = det_time[0] & 0xff;
    denm_update->detection_time[1]      = det_time[1] & 0xff;
    denm_update->detection_time[2]      = det_time[2] & 0xff;
    denm_update->detection_time[3]      = det_time[3] & 0xff;
    denm_update->detection_time[4]      = det_time[4] & 0xff;
    denm_update->detection_time[5]      = det_time[5] & 0xff;

    denm_update->validity_duration[0]   = val_dur[0] & 0xff;
    denm_update->validity_duration[1]   = val_dur[1] & 0xff;
    denm_update->validity_duration[2]   = val_dur[2] & 0xff;

    denm_update->information_quality    = info_qual & 0xff;
    denm_update->cause                  = cause & 0xff;
    denm_update->subcause               = sub_cause & 0xff;
    denm_update->relevance_distance     = rel_dist & 0xff;
    denm_update->relevance_traffic_direction = rel_traf_dir & 0xff;

    denm_update->transmission_interval  = htons(tx_intvl);
    denm_update->repetition_interval    = htons(rep_intvl);

    denm_update->alacarte_length        = alacarte_length & 0xff;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_DENM_UT_DENM_UPDATE_DENM_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)denm_update,
                sizeof(EU_UTDENMUpdateDENMEvent_t) + alacarte_length);

//    ut_tester_process_client_request(ut_priv,
//                EU_UT_MSG_TYPE_DENM_UT_DENM_UPDATE_DENM_RESULT);

    ut_tester_denm_update_log_tx(ut_priv, denm_update);
}

static void
ut_tester_denm_terminate_log_tx(struct ut_tester_priv *ut_priv,
                                EU_UTDENMTerminateDENMEvent_t *denm_terminate)
{
    int      msg_type    = 0;
    uint32_t station_id  = 0;
    int      sequence_no = 0;

    msg_type    = denm_terminate->msg_type;
    station_id  = ntohl(denm_terminate->station_id);
    sequence_no = ntohs(denm_terminate->sequence_no);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%u,%d\n", ++tx_count,
                                                    msg_type,
                                                    station_id,
                                                    sequence_no);
}

static void
ut_denm_terminate_parser(char *data,
                         int len,
                         struct ut_tester_priv *ut_priv)
{
    EU_UTDENMTerminateDENMEvent_t denm_terminate;

    int      ret   = -1;
#if 0
    ret = sscanf(data, "%u,%d", &station_id, &sequence_no);

    if (ret != 2) {
        fprintf(stderr, "Failed to parse DENM Terminate Event\n");
        return;
    }
#endif
    ret = sscanf(data, "%d", &term_denm_index);
    if (ret != 1) {
        fprintf(stderr, "Failed to parse Terminate DENM Event\n");
        return;
    }

    if (!denm_data[term_denm_index].is_valid) {
        fprintf(stderr,
            "No valid DENM present at the index %d\n", term_denm_index);
        return;
    }

    if (term_denm_index < 0 || term_denm_index >= UT_TESTER_MAX_DENMS) {
        fprintf(stderr, "Invalid index for Terminate DENM %d [0, %d]\n",
                                                    term_denm_index,
                                                    UT_TESTER_MAX_DENMS - 1);
        return;
    }

    memset(&denm_terminate, 0, sizeof(denm_terminate));

    denm_terminate.msg_type    = EU_UT_MSG_TYPE_DENM_UT_DENM_TERMINATE_DENM;
    denm_terminate.station_id  = htonl(denm_data[term_denm_index].station_id);
    denm_terminate.sequence_no = htons(denm_data[term_denm_index].sequence_no);

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_DENM_UT_DENM_TERMINATE_DENM_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&denm_terminate,
                                        sizeof(denm_terminate));

//    ut_tester_process_client_request(ut_priv,
//            EU_UT_MSG_TYPE_DENM_UT_DENM_TERMINATE_DENM_RESULT);

    ut_tester_denm_terminate_log_tx(ut_priv, &denm_terminate);
}

static void
ut_mapspat_trigger_func(char *data,
                        int len,
                        struct ut_tester_priv *ut_priv)
{
    int ret;
    int map_spat_event = 0;

    ret = sscanf(data, "%d", &map_spat_event);
    if (ret != 1) {
        fprintf(stderr, "failed to parse mapspat trigger\n");
        return;
    }

    EU_UTMapSpatTrigger_t map_spat_cmd;

    map_spat_cmd.msg_type = EU_UT_MSG_TYPE_MAP_SPAT_TRIGGER;
    map_spat_cmd.event = map_spat_event;

    ut_tester_set_timeout_for_reply();
    exp_msg_type = EU_UT_MSG_TYPE_MAP_SPAT_TRIGGER_RESULT;

    ut_tester_write_command(ut_priv, (uint8_t *)&map_spat_cmd,
                            sizeof(map_spat_cmd));

    //ut_tester_process_client_request(ut_priv, EU_UT_MSG_TYPE_MAP_SPAT_TRIGGER_RESULT);

    UT_TESTER_TX_LOG(ut_priv->tx_fp, "%lu,0x%02x,%d\n", ++tx_count,
                                        (map_spat_cmd.msg_type & 0xff),
                                        (map_spat_cmd.event & 0xff));
}

static void
ut_parse_ts_command(char *data,
                    int len,
                    struct ut_tester_priv *ut_priv)
{
    struct ut_command_list {
        char *string;
        int n_args;
        UT_ARG_TYPE_t arg_type;
        int len;
        void (*parser)(char *data, int len, struct ut_tester_priv *priv);
    } string_list[] = {
        {"ut_init", 1, UT_ARG_TYPE_OCTET_STRING, 8, ut_init_parser_func},

        {"ut_change_pos", 3, UT_ARG_TYPE_DOUBLE, 3, ut_change_pos_func},

        {"ut_cam_change_curvature", 1, UT_ARG_TYPE_SIGNED_INT, 1, ut_cam_curvature_func},
        {"ut_cam_change_speed", 1, UT_ARG_TYPE_SIGNED_INT, 1, ut_cam_speed_func},
        {"ut_cam_set_accel_control_status", 1, UT_ARG_TYPE_SIGNED_INT, 1, ut_cam_set_accel_ctrl_status_func},
        {"ut_cam_set_exterior_lights_status", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_exterior_lights_func},
        {"ut_cam_change_heading", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_change_heading},
        {"ut_cam_set_drive_direction", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_driving_direction},
        {"ut_cam_change_yawrate", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_change_yawrate},
        {"ut_cam_set_station_type", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_station_type},
        {"ut_cam_set_vehiclerole", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_vehiclerole},
        {"ut_cam_set_embarkation_status", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_embarkation_status},
        {"ut_cam_set_pt_activation", 2, UT_ARG_TYPE_STRING, 1, ut_cam_set_pt_activation},
        {"ut_cam_set_dangerous_goods", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_dangerous_goods},
        {"ut_cam_set_lightbar_siren", 1, UT_ARG_TYPE_UNSIGNED_INT, 1, ut_cam_set_lightbar_siren_func},
        {"ut_mapspat_trigger", 1, UT_ARG_TYPE_SIGNED_INT, 1, ut_mapspat_trigger_func},

        {"ut_btp_gen_btpb", 2, UT_ARG_TYPE_UNSIGNED_INT, 4, ut_btpb_gen_parser},

        {"ut_gn_gen_shb", 2, UT_ARG_TYPE_STRING,
              sizeof(EU_UTGnTriggerSHB_t) - sizeof(uint8_t), //Payload length is calculated
              ut_gn_gen_shb_parser},

        {"ut_gn_gen_guc", 3, UT_ARG_TYPE_STRING,
              sizeof(EU_UTGnTriggerGUC_t) - sizeof(uint8_t),
              ut_gn_gen_guc_parser},

        {"ut_gn_gen_gbc", 9, UT_ARG_TYPE_STRING,
              sizeof(EU_UTGnTriggerGBC_t) - sizeof(uint8_t),
              ut_gn_gen_gbc_parser},

        {"ut_gn_gen_gac", 8, UT_ARG_TYPE_STRING,
              sizeof(EU_UTGnTriggerGAC_t) - sizeof(uint8_t),
              ut_gn_gen_gac_parser},

        {"ut_gn_gen_tsb", 3, UT_ARG_TYPE_STRING,
              sizeof(EU_UTGnTriggerTSB_t) - sizeof(uint8_t),
              ut_gn_gen_tsb_parser},

        {"ut_denm_generate_denm_event", 10, UT_ARG_TYPE_STRING,
              sizeof(EU_UTDENMTrigger_t) - sizeof(uint8_t),
              ut_denm_trigger_parser},

        {"ut_denm_update_denm_event", 10, UT_ARG_TYPE_STRING,
              sizeof(EU_UTDENMUpdateDENMEvent_t) - sizeof(uint8_t),
              ut_denm_update_parser},

        {"ut_denm_terminate_denm_event", 2, UT_ARG_TYPE_STRING,
              sizeof(EU_UTDENMTerminateDENMEvent_t) - sizeof(uint8_t),
              ut_denm_terminate_parser},
    };
    int     string_list_len;
    int     i;

    string_list_len = sizeof(string_list) / sizeof(string_list[0]);

    for (i = 0; i < string_list_len; i ++) {
        if (strstr(data, string_list[i].string)) {
            // matched the command ..
            // 1. remove space and take the data input
            // 2. parse according to the data structure defined in the TS 103099
            // 3. fill the data structure
            // 4. forward it over UDP

            int str_len = strlen(string_list[i].string) + 1;

            string_list[i].parser(data + str_len, len - str_len, ut_priv);
        }
    }
}

static int ut_tester_send_command(struct ut_tester_priv *ut_priv)
{
    char data[1024];
    void *res;

    while (1) {
        res = fgets(data, sizeof(data), ut_priv->ts_fp);
        if (!res) { // reading finished
            fclose(ut_priv->ts_fp);
            ut_priv->file_read_complete = 1;
            return 1;
        }

        // skip the line
        if ((data[0] == '\n') ||(data[0] == '#')) {
            continue;
        } else {
            break;
        }
    }

    data[strlen(data) - 1] = '\0';
    ut_parse_ts_command(data, strlen(data) - 1, ut_priv);
    return 0;
}

static void
ut_tester_check_mapspat_trigger_result(struct ut_tester_priv *ut_priv,
                                        uint8_t *msg, int msg_len)
{
    EU_UTMapSpatTriggerResult_t *ut_mapspat_trig_result;

    ut_mapspat_trig_result = (EU_UTMapSpatTriggerResult_t *)msg;

    if (msg_len != sizeof(EU_UTMapSpatTriggerResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_mapspat_trig_result->msg_type);
        return;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                        ut_mapspat_trig_result->msg_type,
                                        ut_mapspat_trig_result->result);
}

static void
ut_tester_check_btp_trigger_result(struct ut_tester_priv *ut_priv,
                                   uint8_t *msg, int msg_len)
{
    EU_UTBtpTriggerResult_t *ut_btp_trig_result;

    ut_btp_trig_result = (EU_UTBtpTriggerResult_t *)msg;

    if (msg_len != sizeof(EU_UTBtpTriggerResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_btp_trig_result->msg_type);
        return;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                        ut_btp_trig_result->msg_type,
                                        ut_btp_trig_result->result);
}

static void
ut_tester_check_gn_trigger_result(struct ut_tester_priv *ut_priv,
                                  uint8_t *msg, int msg_len)
{
    EU_UTGnTriggerResult_t *ut_gn_trig_result;

    ut_gn_trig_result = (EU_UTGnTriggerResult_t *)msg;

    if (msg_len != sizeof(EU_UTGnTriggerResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_gn_trig_result->msg_type);
        return;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                    ut_gn_trig_result->msg_type,
                                    ut_gn_trig_result->result);
}

static void
ut_tester_check_denm_termination_result(struct ut_tester_priv *ut_priv,
                                        uint8_t *msg, int msg_len)
{
    EU_UTDENMTerminationResult_t *ut_denm_term_result;

    ut_denm_term_result = (EU_UTDENMTerminationResult_t *)msg;

    if (msg_len != sizeof(EU_UTDENMTerminationResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_denm_term_result->msg_type);
        return;
    }

    if (ut_denm_term_result->result == EU_UT_RES_PASS) {
        denm_data[term_denm_index].is_valid = 0;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                        ut_denm_term_result->msg_type,
                                        ut_denm_term_result->result);
}

static void
ut_tester_check_denm_update_result(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    uint32_t station_id  = 0;
    uint16_t sequence_no = 0;

    EU_UTDENMTriggerResult_t *ut_denm_update_result;

    ut_denm_update_result = (EU_UTDENMTriggerResult_t *)msg;

    if (msg_len != sizeof(EU_UTDENMTriggerResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_denm_update_result->msg_type);
        return;
    }

    station_id  = ntohl(ut_denm_update_result->stationid);
    sequence_no = ntohs(ut_denm_update_result->sequenceno);

    if (ut_denm_update_result->result == EU_UT_RES_PASS) {
        denm_data[update_denm_index].station_id  = station_id;
        denm_data[update_denm_index].sequence_no = sequence_no;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d,%u,%d\n", ++resp_count,
                                ut_denm_update_result->msg_type,
                                ut_denm_update_result->result,
                                station_id,
                                sequence_no);
}

static void
ut_tester_check_denm_trigger_result(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    uint32_t    station_id  = 0;
    uint16_t    sequence_no = 0;

    EU_UTDENMTriggerResult_t *ut_denm_trig_result;

    ut_denm_trig_result = (EU_UTDENMTriggerResult_t *)msg;

    if (msg_len != sizeof(EU_UTDENMTriggerResult_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                ++resp_count, ut_denm_trig_result->msg_type);
        return;
    }

    station_id  = ntohl(ut_denm_trig_result->stationid);
    sequence_no = ntohs(ut_denm_trig_result->sequenceno);

    if (ut_denm_trig_result->result == EU_UT_RES_PASS) {
        denm_data[new_denm_index].is_valid    = 1;
        denm_data[new_denm_index].station_id  = station_id;
        denm_data[new_denm_index].sequence_no = sequence_no;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d,%u,%d\n", ++resp_count,
                                ut_denm_trig_result->msg_type,
                                ut_denm_trig_result->result,
                                station_id,
                                sequence_no);
}

static void
ut_tester_check_cam_trigger_result(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTResp_t *ut_cam_resp;

    ut_cam_resp = (EU_UTResp_t *)msg;

    if (msg_len != sizeof(EU_UTResp_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                        ++resp_count, ut_cam_resp->msg_type);
        return;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                            ut_cam_resp->msg_type, ut_cam_resp->result);
}

static void
ut_tester_check_ut_change_pos_response(struct ut_tester_priv *ut_priv,
                                        uint8_t *msg, int msg_len)
{
    EU_UTResp_t *ut_resp;

    ut_resp = (EU_UTResp_t *)msg;

    if (msg_len != sizeof(EU_UTResp_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                            ++resp_count, ut_resp->msg_type);
        return;
    }

    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                    ut_resp->msg_type, ut_resp->result);
}

static void
ut_tester_check_ut_init_response(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTResp_t *ut_resp;

    ut_resp = (EU_UTResp_t *)msg;

    if (msg_len != sizeof(EU_UTResp_t)) {

        UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,Invalid Packet Size\n",
                                            ++resp_count, ut_resp->msg_type);
        return;
    }
    UT_TESTER_RESP_LOG(ut_priv->resp_fp, "%lu,0x%02x,%d\n", ++resp_count,
                                    ut_resp->msg_type, ut_resp->result);
    //XXX: Exit if failed, since stack is uninitialized
}

static void
ut_tester_process_spat_event_indication(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTMapSpatEventIndication_t *ut_spat_ind;

    ut_spat_ind = (EU_UTMapSpatEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_spat_ind->msg_type,
                             ut_spat_ind->packet,
                             ntohs(ut_spat_ind->packet_length));
}

static void
ut_tester_process_map_event_indication(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTMapSpatEventIndication_t *ut_map_ind;

    ut_map_ind = (EU_UTMapSpatEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_map_ind->msg_type,
                             ut_map_ind->packet,
                             ntohs(ut_map_ind->packet_length));
}

static void
ut_tester_process_btp_event_indication(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTBtpEventIndication_t *ut_btp_ind;

    ut_btp_ind = (EU_UTBtpEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_btp_ind->msg_type,
                             ut_btp_ind->packet,
                             ntohs(ut_btp_ind->packet_length));
}

static void
ut_tester_process_gn_event_indication(struct ut_tester_priv *ut_priv,
                                    uint8_t *msg, int msg_len)
{
    EU_UTGnEventIndication_t *ut_gn_ind;

    ut_gn_ind = (EU_UTGnEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_gn_ind->msg_type,
                             ut_gn_ind->packet,
                             ntohs(ut_gn_ind->packet_length));
}

static void
ut_tester_process_denm_event_indication(struct ut_tester_priv *ut_priv,
                                            uint8_t *msg, int msg_len)
{
    EU_UTDENMEventIndication_t *ut_den_ind;

    ut_den_ind = (EU_UTDENMEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_den_ind->msg_type,
                             ut_den_ind->denm_pdu,
                             ntohs(ut_den_ind->denm_pdu_length));
}

static void
ut_tester_process_cam_event_indication(struct ut_tester_priv *ut_priv,
                                        uint8_t *msg, int msg_len)
{
    EU_UTCamEventIndication_t *ut_cam_ind;

    ut_cam_ind = (EU_UTCamEventIndication_t *)msg;

    ut_tester_log_indication(ut_priv,
                             ut_cam_ind->msg_type,
                             ut_cam_ind->cam_pdu,
                             ntohs(ut_cam_ind->cam_pdu_len));
}

static void
ut_tester_process_client_request(struct ut_tester_priv *ut_priv)
{
    int     ret;
    fd_set  rdfd;
    uint8_t data[2000];

    struct ut_tester_msg {
        uint8_t msgtype;
        uint8_t data[0];
    } __attribute__ ((__packed__));

    while (1) {

        //pthread_mutex_lock(&mutex);
        sem_wait(&s2);

        rdfd = ut_priv->allfd;

        ret = select(ut_priv->maxfd + 1, &rdfd, NULL, NULL, &tv);
        if (ret < 0) {
            fprintf(stderr, "Error in select\n");
            //exit(1);
        } else if ((ret == 0) && (exp_msg_type != 0xFF)) {
            UT_TESTER_RESP_LOG(ut_priv->resp_fp,
                              "%lu,0x%02x,No Response from SUT\n",
                              ++resp_count, exp_msg_type);

            if (exp_msg_type == EU_UT_MSG_TYPE_UT_INIT_RESP) {
                fprintf(stderr, "Failed to recv SUT init status\n");
                //exit(1); //Since stack init failed
            }
            exp_msg_type = 0xFF;

            sem_post(&s1);
            //pthread_mutex_unlock(&mutex);
            continue;
        }

        if (!FD_ISSET(ut_priv->sock, &rdfd)) {
            //pthread_mutex_unlock(&mutex);
            sem_post(&s1);
            continue; //A small sleep may be required. Otherwise CPU usage goes high if there is no packet
        }

        ret = recvfrom(ut_priv->sock, data, sizeof(data), 0, NULL, NULL);
        if (ret < 0) {
            fprintf(stderr, "failed to recvfrom SUT\n");
            //pthread_mutex_unlock(&mutex);
            sem_post(&s1);
            return; //need to exit here
        }

        struct ut_tester_msg *msg;

        msg = (struct ut_tester_msg *)data;

        switch (msg->msgtype) {

            case EU_UT_MSG_TYPE_UT_INIT_RESP:

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_ut_init_response(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_CHANGE_POS_RESP: // change position response

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_ut_change_pos_response(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_CAM_EVENT_INDICATION: // CAM event indication

                ut_tester_process_cam_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_DENM_UT_DENM_EVENT_INDICATION: // DENM event indication

                ut_tester_process_denm_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_GN_TRIGGER_EVENT_INDICATION: // GN event indication

                ut_tester_process_gn_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_BTP_EVENT_INDICATION: // BTP event indication

                ut_tester_process_btp_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_MAP_EVENT_INDICATION: // MAP event indication

                ut_tester_process_map_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_SPAT_EVENT_INDICATION: // SPAT event indication

                ut_tester_process_spat_event_indication(ut_priv, data, ret);
                break;

            case EU_UT_MSG_TYPE_CAM_TRIGGER_RESULT: // CAM trigger result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_cam_trigger_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_DENM_UT_DENM_TRIGGER_RESULT: // DENM trigger result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_denm_trigger_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_DENM_UT_DENM_UPDATE_DENM_RESULT: // DENM update result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_denm_update_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_DENM_UT_DENM_TERMINATE_DENM_RESULT: // DENM terminate result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_denm_termination_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_GN_TRIGGER_RESULT: // GN trigger result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_gn_trigger_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_BTP_TRIGGER_RESULT: // BTP trigger result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_btp_trigger_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            case EU_UT_MSG_TYPE_MAP_SPAT_TRIGGER_RESULT: // MAPSPAT trigger result

                if (exp_msg_type == msg->msgtype) {
                    ut_tester_check_mapspat_trigger_result(ut_priv, data, ret);
                    exp_msg_type = 0xFF;
                    timerclear(&tv);
                }
                break;

            default:
                fprintf(stderr, "invalid response 0x%x received\n",
                                        msg->msgtype);
        }
        //pthread_mutex_unlock(&mutex);
        sem_post(&s1);
    }
}

void *ut_tester_recv(void *data)
{
    struct ut_tester_priv *ut_priv;

    ut_priv = (struct ut_tester_priv *)data;

    ut_tester_process_client_request(ut_priv);

    return NULL;
}

void *ut_tester_send_request(void *data)
{
    int ret;

    struct ut_tester_priv *ut_priv;

    ut_priv = (struct ut_tester_priv *)data;

    while (1) {
        sem_wait(&s1);

        struct timeval send_timeout = {
            .tv_sec = 0,
            .tv_usec = 1000 * 1000
        };

        ret = select(1, NULL, NULL, NULL, &send_timeout);
        if (ret < 0) {
            fprintf(stderr, "Error in select\n");
        } else if ((ret == 0) && (ut_priv->file_read_complete == 0)) { //at every timer event .. read the commands and push them over to the socket
            //pthread_mutex_lock(&mutex);
            //sem_wait(&s1);
            ut_tester_send_command(ut_priv);
            //sem_post(&s2);
            //pthread_mutex_unlock(&mutex);
        }

        if (ut_priv->file_read_complete)
            fprintf(stderr, "file reading complete\n");

        sem_post(&s2);
    }
    return NULL;
}

static int ut_tester_loop(struct ut_tester_priv *ut_priv)
{

    //pthread_mutex_init(&mutex, NULL);

    sem_init(&s1, 0, 1);
    sem_init(&s2, 0, 0);

    pthread_create(&t1, NULL, ut_tester_send_request, ut_priv);
    pthread_create(&t2, NULL, ut_tester_recv, ut_priv);

    pthread_join(t2, NULL);
    pthread_join(t1, NULL);

    sem_destroy(&s1);
    sem_destroy(&s2);
    //pthread_mutex_destroy(&mutex);

    pthread_exit(NULL);
    return 0;
}

static void ut_tester_event_log_create(struct ut_tester_priv *ut_priv)
{
    ut_priv->event_fp = fopen("event_log.utlog", "w");
    if (!ut_priv->event_fp) {
        ut_priv->event_fp = stderr;
        return;
    }
}

static void ut_tester_tx_log_create(struct ut_tester_priv *ut_priv)
{
    ut_priv->tx_fp = fopen("tx_log.utlog", "w");
    if (!ut_priv->tx_fp) {
        ut_priv->tx_fp = stderr;
        return;
    }
}

static void ut_tester_resp_log_create(struct ut_tester_priv *ut_priv)
{
    ut_priv->resp_fp = fopen("resp_log.utlog", "w");
    if (!ut_priv->resp_fp) {
        ut_priv->resp_fp = stderr;
        return;
    }
}

int main(int argc, char **argv)
{
    char    *ip = NULL;
    int     port = 1999;
    char    *logfile_name = NULL;
    char    *ts_name = NULL;
    int     ret;
    struct  ut_tester_priv ut_priv;

    memset(&ut_priv, 0, sizeof(struct ut_tester_priv));

    while ((ret = getopt(argc, argv, UT_TESTER_OPTS)) != -1) {
        switch (ret) {
            case 'i':
                ip = optarg;
            break;
            case 'p':
                port = atoi(optarg);
                if ((port < 0) || (port > 65535)) {
                    usage(argv[0]);
                    return -1;
                }
            break;
            case 'l':
                logfile_name = optarg;
            break;
            case 'f':
                ts_name = optarg;
            break;
            default:
                usage(argv[0]);
                return -1;
        }
    }

    if (!ip) {
        fprintf(stderr, "Parse Ip address with -i\n");
        usage(argv[0]);
        return -1;
    }

    if (!ts_name) {
        fprintf(stderr, "Parse UT script with -f\n");
        usage(argv[0]);
        return -1;
    }

    ret = ut_tester_setup_client_sock(&ut_priv, ip, port);
    if (ret < 0) {
        fprintf(stderr, "failed to setup client socket\n");
        return -1;
    }

    ut_priv.ts_fp = fopen(ts_name, "r");
    if (!ut_priv.ts_fp) {
        fprintf(stderr, "failed to open %s\n", ts_name);
        return -1;
    }

    ut_tester_event_log_create(&ut_priv);
    ut_tester_tx_log_create(&ut_priv);
    ut_tester_resp_log_create(&ut_priv);

    ut_tester_loop(&ut_priv);
    return 0;
}

