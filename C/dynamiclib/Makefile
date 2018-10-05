all:
	gcc -fPIC -c func.c func2.c
	gcc -shared -fPIC -o libx.so func.o func2.o
	gcc -o main main_func.c -L. -lx -Wl,-rpath,`pwd`

clean:
	@rm -rf *.o *.so main
