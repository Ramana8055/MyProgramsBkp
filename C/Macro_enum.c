#define FOREACH_FRUIT(FRUIT) \
        FRUIT(apple)   \
        FRUIT(orange)  \
        FRUIT(grape)   \
        FRUIT(banana)  \

#define GENERATE_ENUM(ENUM) ENUM,
#define GENERATE_STRING(STRING) #STRING,

enum FRUIT_ENUM {
    FOREACH_FRUIT(GENERATE_ENUM)
};

static const char *FRUIT_STRING[] = {
    FOREACH_FRUIT(GENERATE_STRING)
};
