#include <linux/ioctl.h>

#define SCULL_MAGIC 'm'
#define SCULL_IO_ONE    _IO(SCULL_MAGIC, 0)
#define SCULL_IO_TWO    _IO(SCULL_MAGIC, 1)
#define SCULL_IO_THREE  _IO(SCULL_MAGIC, 2)
#define SCULL_IO_FOUR   _IO(SCULL_MAGIC, 3)
#define SCULL_IO_FIVE   _IO(SCULL_MAGIC, 4)
