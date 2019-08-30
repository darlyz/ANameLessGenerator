# makefile for FELAC, implemented in ANSI C
CC = gcc
FLAGS = -Wall -c
NAME = CFLAG
LIBS = -L"%pfelacpath%/lib/" -lfelac -L"%pfelacpath%/solv/SuperLU/" -lsuperlu
SOLV = -L"%pfelacpath%/solv/AztecOO/" -laztec -L"%pfelacpath%/solv/CLAPACK/" -llapack
OBJS = testw4.c \
gidmsh.c gidres.c gidpre.c utestw4a.c etestw4a.c starta.c aew4g2.c solv.c epgsub.c 
 
#SRC = $(wildcard *.c)
obj = $(patsubst %.c,%.o,$(OBJS))
 
testw4: $(obj)
	gcc $(obj) -o testw4 $(LIBS) $(SOLV) -lm
$(obj):%.o:%.c
	gcc -std=c99 -c $< -o $@
 
.PHONY: clean
clean:
	del testw4 testw4.exe *.o *.obj
