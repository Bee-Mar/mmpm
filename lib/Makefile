all: lib

lib: mmpm.o fort.o shared_object

mmpm.o: mmpm.c
	gcc -c -fPIC mmpm.c -o mmpm.o

fort.o: fort.c
	gcc -c -fPIC fort.c -o fort.o

shared_object: mmpm.o fort.o
	gcc -shared -Wl,-soname,libmmpm.so -o libmmpm.so mmpm.o fort.o

clean:
	rm -f libmmpm.so fort.o mmpm.o
