obj-m 	+= cdev_driv.o

all:
	make -C /lib/modules/$(shell uname -r)/build/ M=$(PWD) modules
	gcc sample.c -o sample
	dmesg -C
	insmod cdev_driv.ko

clean:
	make -C /lib/modules/$(shell uname -r)/build/ M=$(PWD) clean
	rm -f sample
	dmesg -C
	rmmod cdev_driv
