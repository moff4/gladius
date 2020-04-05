G=gcc
F=-Wall --shared -O3 -fPIC 

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	F += -Wl,-soname,
endif
ifeq ($(UNAME_S),Darwin)
	F += -Wl,-install_name,
endif

S=src/utils.c
H=include/utils.h
I=include/


all: utils.so

utils.so: $S $H
	$G -I$I $S $Futils -o utils.so

clean:
	rm -rf *.o
	rm -rf *.so
	rm -rf *.a
