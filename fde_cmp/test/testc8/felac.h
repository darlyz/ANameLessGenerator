#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "solver.h"
#define maxtype 20
#define maxnode 10000000
#define maxmate 10000
#define endl '\n'
#define time time_now
#ifndef null
#ifdef __cplusplus
#define null 0
#else
#define null ((void*)0)
#endif
#endif
struct coordinates
{
    int dim,knode;
    double *coor;
};
struct matrice
{
    int neq,maxa,*numcol,*na,*jdiag;
    double *a;
};
struct element
{
    int ntype,nelem[maxtype],nmate[maxtype],nnode[maxtype],nprmt[maxtype];
    int *node;
    double *mate;
};
int nbdetype,end,stop,it,itn,itnmax,imate,nmate,nprmt,nelem,ityp,inod,idof;
int nstep;
double tolerance,dampalfa,dampbeta;
double dt,time_now,tmax;
struct coordinates coor0, coor1;
int print(const char *__format, ...);
int inita,dofa,initb,dofb,dim;
int *ida,*idb;
int *maplga,*imaplga,*maplgb,*imaplgb;
double *unoda,*unodb;
double *ubfa,*ubfb;
double *dispa,*dispb;
double *fa,*fb;
struct element elema,elemb;
struct matrice matrixa,matrixb;

