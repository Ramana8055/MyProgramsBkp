#include<linux/init.h>
#include<linux/module.h>
#include<linux/kernel.h>
#include<linux/types.h>
#include<linux/fs.h>
#include<linux/cdev.h>
#include<linux/uaccess.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("RAMANA");



static struct cdev mydev;
static dev_t mydevnum;

static int scull_open(struct inode* inodeptr,struct file* fptr){
	printk(KERN_ALERT "opened!!\n");
	return 0;
}

static int scull_release(struct inode* inodeptr,struct file* fptr){
	printk(KERN_ALERT "closed!!\n");
	return 0;
}

static ssize_t scull_read(struct file *fptr,char __user *usrptr,size_t count,loff_t* fpos){
	if(copy_to_user(usrptr,"Hello, This is kernel\n",23)){
		printk(KERN_ALERT "copy_to_user failed\n");
		return -EFAULT;
	}
	return count;
}

static ssize_t scull_write(struct file* ffptr,const char __user *usrptr,size_t count ,loff_t* fpos){
	char a[256]="";
	copy_from_user(a,usrptr,count);
	return count;
}

static struct file_operations fop={
	.owner=THIS_MODULE,
	.open=scull_open,
	.release=scull_release,
	.read=scull_read,
	.write=scull_write
};

static int scull_init(void){
	int err=0;
	/*dev_t*/ mydevnum=MKDEV(101,0);
	err=register_chrdev_region(mydevnum,1,"scull2");
	if(err){
		printk(KERN_ALERT "Can't register\n");
		return err;
	}

	cdev_init(&mydev,&fop);
	mydev.owner=THIS_MODULE;

	err=cdev_add(&mydev,mydevnum,1);
	if(err){
		printk(KERN_ALERT "Couldn't add device\n");
		unregister_chrdev_region(mydevnum,1);
		return err;
	}
	printk(KERN_ALERT "Module is inserted\n");
	return 0;
}

static void scull_exit(void){
	cdev_del(&mydev);
	unregister_chrdev_region(mydevnum,1);
	printk(KERN_ALERT "Module unloaded\n");
}
module_init(scull_init);
module_exit(scull_exit);
