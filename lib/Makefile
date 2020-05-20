DESTINATION=/usr/local/lib/mmpm
CC=gcc

all: lib

lib: mmpm.o fort.o shared_object

mmpm.o: mmpm.c
	$(CC) -c -fPIC mmpm.c -o mmpm.o

fort.o: fort.c
	$(CC) -c -fPIC fort.c -o fort.o

shared_object: mmpm.o fort.o
	$(CC) -shared -Wl,-soname,libmmpm.so -o libmmpm.so mmpm.o fort.o

clean:
	rm -f libmmpm.so fort.o mmpm.o

install:
	sudo mkdir -p $(DESTINATION)
	sudo install libmmpm.so $(DESTINATION)
