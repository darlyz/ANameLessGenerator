/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = bft.c
Version:2.2
Time of release:2019-06-18 17:21:30
All rights reserved by ECTEC Corporation, and person or
organization using Original software to generated these code,anyone
else must get written permission from ECTEC Corporation to
copy a part or whole of this code.
The Code GenID is:
22565914_000906E9071008007FFAFBFFBFEBFBFF_005056C00008
Copyright is protected from:2017-2030
**************************************************************/
/*
时间更新程序：
1、给出当前时刻、当前时间步；
2、判断是否达到终止时刻；
3、提供依赖时间变化的边值和节点荷载条件的函数。
*/
#include "felac.h"
/* 动态边界条件计算的函数声明 */
void bftbound(struct coordinates,int,int,int*,double*);
void bftforce(struct coordinates,int,int,int*,double*);
//double fbound(double*,double,int,int,double);
//double fforce(double*,double,int,int,double);
void bft()
{
    /*
    变量解释:
    time_now: 当前计算时间；
    it:   当前时间步；
    end:  非线性迭代标志；
    stop: 时间是否结束的标志。
    */
    time_now += dt;
    it   += 1;
    end   = 0;
    print("time_now,it=%f,%d%c",time_now,it,endl);
    /* 判断是否计算结束，stop=0表示计算未结束，stop=1表示该时间步计算完成后程序结束 */
    if (time_now<tmax)
    {
        stop = 0;
    }
    else
    {
        stop = 1;
    }
//bftbound(coor0,1,dofa,ida,ubfa);
//bftforce(coor0,1,dofa,ida,ubfa);
    return;
}
/*  bftbound:动态边界条件计算的函数  */
void bftbound(coor0,nf,dof,nv,bf)
struct coordinates coor0;
int nf,dof,*nv;
double *bf;
{
    int dim,knode,n,j,id;
    double *coor,*r,bfold;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    r = (double *) calloc(dim+1,sizeof(double));
    for (n=1; n<=knode; n++)
    {
        for (j=1; j<=dim; j++)
        {
            r[j] = coor[(j-1)*(knode)+n-1];
        }
        for (j=1; j<=dof; j++)
        {
            id = nv[(j-1)*(knode)+n-1];
//if (id<0) bfold = bf[(j-1)*(knode)+n-1];
//if (id<0) bf[(j-1)*(knode)+n-1] = fbound(r,time_now,j,nf,bfold);
        }
    }
    free(r);
}
/*  bftforce:动态节点荷载计算的函数  */
void bftforce(coor0,nf,dof,nv,bf)
struct coordinates coor0;
int nf,dof,*nv;
double *bf;
{
    int dim,knode,n,j,id;
    double *coor,*r,bfold;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    r = (double *) calloc(dim+1,sizeof(double));
    for (n=1; n<=knode; n++)
    {
        for (j=1; j<=dim; j++)
        {
            r[j] = coor[(j-1)*(knode)+n-1];
        }
        for (j=1; j<=dof; j++)
        {
            id = nv[(j-1)*(knode)+n-1];
//if (id>0) bfold = bf[(j-1)*(knode)+n-1];
//if (id>0) bf[(j-1)*(knode)+n-1] = fforce(r,time_now,j,nf,bfold);
        }
    }
    free(r);
}
