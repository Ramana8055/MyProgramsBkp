obj-m		:= km.o 
KERN_SRC	:= /lib/modules/$(shell uname -r)/build/
PWD			:= $(shell pwd)

modules:
	make -C $(KERN_SRC) M=$(PWD) modules
	@gcc -o x ./x.c

install:
	make -C $(KERN_SRC) M=$(PWD) modules_install
	@depmod -a

clean:
	make -C $(KERN_SRC) M=$(PWD) clean
	@rm -f x
i:
	@insmod km.ko
r:
	@rmmod km
c:
	@dmesg -c >/dev/null
