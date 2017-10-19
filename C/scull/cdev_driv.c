#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <asm/uaccess.h>
#include "ioctl_base.h"

MODULE_DESCRIPTION("SCULL");
MODULE_AUTHOR("Ramana");
MODULE_LICENSE("GPL");

#define NUM_MINORS (1)

static int major_no = 236;
static dev_t dev;
static struct cdev scull_cdev;

static int scull_open(struct inode *inode, struct file *file)
{
    printk(KERN_INFO "Device opened\n");
    return 0;
}

static int scull_close(struct inode *inode, struct file *file)
{
    printk(KERN_INFO "Device closed\n");
    return 0;
}

static long scull_ioctl(struct file *file, unsigned int cmd, unsigned long i)
{
    switch(cmd) {
        case SCULL_IO_ONE:
            printk(KERN_INFO "in scull ioctl one\n");
            break;
        case SCULL_IO_TWO:
            printk(KERN_INFO "in scull ioctl two\n");
            break;
        case SCULL_IO_THREE:
            printk(KERN_INFO "in scull ioctl three\n");
            break;
        case SCULL_IO_FOUR:
            printk(KERN_INFO "in scull ioctl four\n");
            break;
        case SCULL_IO_FIVE:
            printk(KERN_INFO "in scull ioctl five\n");
            break;
    }
    return 0;
}

static ssize_t scull_read(struct file *file, char *buf, size_t size, loff_t *off)
{
    printk(KERN_INFO "Scull Read\n");

    return copy_to_user(buf, "Read", 5) ? -EFAULT : 0;
}

static ssize_t scull_write(struct file *file, const char *buf, size_t size, loff_t *off)
{
    printk(KERN_INFO "Scull Write\n");
    printk(KERN_INFO "User data : %s\n", buf);
    return 4;
}

static struct file_operations fops = {
    .open               = scull_open,
    .release            = scull_close,
    .unlocked_ioctl     = scull_ioctl,
    .read               = scull_read,
    .write              = scull_write,
};

static int __init scull_init(void)
{
    int ret = EINVAL;
    int devno = 0;

    dev = MKDEV(major_no, 0);

    printk(KERN_INFO "Scull init\n");

    ret = register_chrdev_region(dev, NUM_MINORS, "scull");
    if (ret < 0) {
        printk(KERN_INFO "Failed to allocate chrdev region\n");
        return ret;
    }

    devno = MKDEV(major_no, 0);

    cdev_init(&scull_cdev, &fops);

    scull_cdev.owner = THIS_MODULE;
    scull_cdev.ops   = &fops;

    ret = cdev_add(&scull_cdev, devno, 1);
    if (ret) {
        printk(KERN_INFO "cdev_add failed\n");
        unregister_chrdev_region(dev, NUM_MINORS);
        return ret;
    }

    return 0;
}

static void __exit scull_exit(void)
{
    printk(KERN_INFO "Scull Exit\n");

    cdev_del(&scull_cdev);
    unregister_chrdev_region(dev, NUM_MINORS);
}

module_init(scull_init);
module_exit(scull_exit);

