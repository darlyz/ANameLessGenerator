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
ʱ����³���
1��������ǰʱ�̡���ǰʱ�䲽��
2���ж��Ƿ�ﵽ��ֹʱ�̣�
3���ṩ����ʱ��仯�ı�ֵ�ͽڵ���������ĺ�����
*/
#include "felac.h"
/* ��̬�߽���������ĺ������� */
void bftbound(struct coordinates,int,int,int*,double*);
void bftforce(struct coordinates,int,int,int*,double*);
//double fbound(double*,double,int,int,double);
//double fforce(double*,double,int,int,double);
void bft()
{
    /*
    ��������:
    time_now: ��ǰ����ʱ�䣻
    it:   ��ǰʱ�䲽��
    end:  �����Ե�����־��
    stop: ʱ���Ƿ�����ı�־��
    */
    time_now += dt;
    it   += 1;
    end   = 0;
    print("time_now,it=%f,%d%c",time_now,it,endl);
    /* �ж��Ƿ���������stop=0��ʾ����δ������stop=1��ʾ��ʱ�䲽������ɺ������� */
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
/*  bftbound:��̬�߽���������ĺ���  */
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
/*  bftforce:��̬�ڵ���ؼ���ĺ���  */
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
