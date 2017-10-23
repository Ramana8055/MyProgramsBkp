#include<linux/module.h>
#include<linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("RAMANA");

static int __init r_init(void)
{
    printk(KERN_INFO"in init function\n");
    return 0;
}

static void __exit r_exit(void)
{
    printk(KERN_INFO"in exit function\n");
}

module_init(r_init);
module_exit(r_exit);
