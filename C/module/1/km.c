#include<linux/kernel.h>
#include<linux/init.h>
#include<linux/module.h>
MODULE_LICENSE("GPL");
MODULE_AUTHOR("RAMANA");

static int __init km_init(void)
{
	printk(KERN_INFO"init_func\n");
	return 0;
}

static void __exit km_exit(void)
{
	printk(KERN_INFO"exit_funcion\n");
}
module_init(km_init);
module_exit(km_exit);
