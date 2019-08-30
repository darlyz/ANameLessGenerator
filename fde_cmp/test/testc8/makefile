# makefile for FELAC, implemented in ANSI C
CC = gcc
FLAGS = -Wall -c
NAME = CFLAG
LIBS = -L"%pfelacpath%/lib/" -lfelac -L"%pfelacpath%/solv/SuperLU/" -lsuperlu
SOLV = -L"%pfelacpath%/solv/AztecOO/" -laztec -L"%pfelacpath%/solv/CLAPACK/" -llapack
OBJS = testc8.c \
gidmsh.c gidres.c gidpre.c utestc8a.c etestc8a.c starta.c aec8g2.c solv.c epgsub.c 
 
#SRC = $(wildcard *.c)
obj = $(patsubst %.c,%.o,$(OBJS))
 
testc8: $(obj)
	gcc $(obj) -o testc8 $(LIBS) $(SOLV) -lm
$(obj):%.o:%.c
	gcc -std=c99 -c $< -o $@
 
.PHONY: clean
clean:
	del testc8 testc8.exe *.o *.obj
