/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = ucheck3a.c
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
后处理计算程序：
1、解向量扩充，将施加了强制性条件的边界上的自由度扩充到求解器解出来的解向量中；
2、若是非线性问题，则对解进行调整，求出当前迭代步的结果；
3、判断是否收敛，若收敛则迭代标识符end置1。
*/
#include "felac.h"
double *unodg;
/* subroutine */
void ucheck3a(coor0,dof,nodvar,u,f)
int dof,*nodvar;
double *u,*f;
struct coordinates coor0;
{
    /*
    变量解释：
     dim：   坐标维度
     knode： 节点总数
     kvar:   总自由度数；
     dof：   该场每个节点的自由度数；
    *coor：  节点坐标空间；
    *nodvar：该场节点自由度对应的规格数或者方程号；
    */
    int i,j,n,nrw,kvar;
    int dim,knode;
    double *coor;
    double *vectu1,*vectu,*vectue,*vectdu;
    double *vectgu;
    double aa,bb,ab,rab,err,ul;
    static double cc;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode*dof;
    vectu1 = (double *) calloc(kvar,sizeof(double));
    vectu = (double *) calloc(kvar,sizeof(double));
    vectue = (double *) calloc(kvar,sizeof(double));
    vectdu = (double *) calloc(kvar,sizeof(double));
    vectgu = (double *) calloc(kvar,sizeof(double));
    /*  解向量扩充，将施加了强制性条件的边界上的自由度扩充到求解器解出来的解向量中； */
    for (i=1; i<=dof; ++i)
        for (j=1; j<=knode; ++j)
        {
            vectu[(i-1)*(knode)+j-1] = u[(i-1)*(knode)+j-1];
            n = nodvar[(i-1)*(knode)+j-1];
            if (n>0)
                vectu[(i-1)*(knode)+j-1] = f[n];
        }
//mpi_sere(knode,dof,vectu);
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectu1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectdu[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
// === ue: 当前步位移结果与上一迭代步的差值，即当前迭代步增量 ===
    for (inod=1; inod<=knode; ++inod)
        for (idof=1; idof<=dof; ++idof)
            vectue[(idof-1)*(knode)+inod-1]=vectu[(idof-1)*(knode)+inod-1]-vectu1[(idof-1)*(knode)+inod-1];
    aa = 0.0;
    ab = 0.0;
    bb = 0.0;
// ===============================================================
// =    对所有节点(nod)和自由度(dof)循环                         =
// =-------------------------------------------------------------=
// =    aa：当前迭代步增量ue的模的平方的和                       =
// =    ab：当前迭代步增量ue与上一迭代步增量du内积的和           =
// =    bb：上一迭代步增量du的模的平方的和                       =
// ===============================================================
    for (inod=1; inod<=knode; ++inod)
    {
        for (idof=1; idof<=dof; ++idof)
        {
            aa = aa+vectue[(idof-1)*(knode)+inod-1]*vectue[(idof-1)*(knode)+inod-1];
            ab = ab+vectue[(idof-1)*(knode)+inod-1]*vectdu[(idof-1)*(knode)+inod-1];
            bb = bb+vectdu[(idof-1)*(knode)+inod-1]*vectdu[(idof-1)*(knode)+inod-1];
        }
    }
//mpi_sum_dou(&aa);
//mpi_sum_dou(&ab);
//mpi_sum_dou(&bb);
    err = aa;                         // err 为当前迭代步误差
    if (itn==1) cc = 1.0;             // 迭代第一步取松弛因子为 1
    if (itn>1)                        // 下面每一迭代步都调整松弛因子
    {
        rab = sqrt(aa)*sqrt(bb);          // 当前增量ue与上一增量du模乘积
        if (ab>0.5*rab) cc = cc*2.0;      // 若ue与du夹角小于60°，松弛因子增倍
        if (ab>0.8*rab) cc = cc*2.0;      // 若ue与du夹角小于37°，松弛因子再次增倍
        if (ab<0.0) cc = cc*0.5;          // 若ue与du夹角大于90°，松弛因子减半
        if (ab<-0.40*rab) cc = cc*0.5;    // 若ue与du夹角大于114°，松弛因子再次减半
        if (ab<-0.80*rab) cc = cc*0.5;    // 若ue与du夹角大于143°，松弛因子再次减半
    }                                 //
    if (cc>1.0) cc = 1.0;             // 控制松弛因子不能大于1
    ul = 0.0;
    for (inod=1; inod<=knode; ++inod)
    {
        for (idof=1; idof<=dof; ++idof)
        {
// === 根据松弛因子(cc)更新迭代步增量 ===
            vectue[(idof-1)*(knode)+inod-1] = vectue[(idof-1)*(knode)+inod-1]*cc;
// === 计算本迭代步松弛后的结果u1 ===
            vectu1[(idof-1)*(knode)+inod-1] = vectu1[(idof-1)*(knode)+inod-1]+vectue[(idof-1)*(knode)+inod-1];
// === 计算本迭代步松弛后结果u的模平方的和ul ===
            ul = ul + vectu1[(idof-1)*(knode)+inod-1]*vectu1[(idof-1)*(knode)+inod-1];
        }
    }
//mpi_sum_dou(&ul);
// ===================================================================
// =    收敛判断                                                     =
// =    err足够小，或者err相对于计算结果的模的平方的和足够小         =
// =    或者迭代步数超出最大迭代步，都会被判断为收敛，停止迭代       =
// =    end为迭代收敛标志变量。                                      =
// ===================================================================
    if (err<tolerance || err<tolerance*ul || itn>itnmax) end = 1;
//mpi_min_int(&end);
    if (end==1)                       // 如果收敛
    {
        for (i=1; i<=knode; ++i)
            for (j=1; j<=dim; ++j)
                coor[(j-1)*(knode)+i-1] += vectu1[(j-1)*(knode)+i-1];
        if (time_now<1.5*dt)                  // 如果时间步为第一时间步
        {
// === 总位移取初值：0.0 ===
            for (inod=1; inod<=knode; ++inod)
                for (idof=1; idof<=dof; ++idof)
                    vectgu[(idof-1)*(knode)+inod-1]=0.0;
// === 将总位移gu写入unodg中 ===
            n=0;
            n=n+dof;
            unodg = (double *) calloc(n*knode,sizeof(double));
            nrw = 0*dof;
            for (j=1; j<=dof; ++j)
                for (i=1; i<=knode; ++i)
                    unodg[(nrw+j-1)*knode+i-1] = vectgu[(j-1)*(knode)+i-1];
            nrw += dof;
        }
        else
        {
// === 读取 ===
            nrw = 0*dof;
            for (j=1; j<=dof; ++j)
                for (i=1; i<=knode; ++i)
                    vectgu[(j-1)*(knode)+i-1] = unodg[(nrw+j-1)*knode+i-1];
            nrw += dof;
        }
// === 计算当前载荷步总位移 ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectgu[(idof-1)*(knode)+inod-1]=vectgu[(idof-1)*(knode)+inod-1]+vectu1[(idof-1)*(knode)+inod-1];
// === 将当前载荷步总位移存储到unodg中 ===
        n=0;
        n=n+dof;
        nrw = 0*dof;
        for (j=1; j<=dof; ++j)
            for (i=1; i<=knode; ++i)
                unodg[(nrw+j-1)*knode+i-1] = vectgu[(j-1)*(knode)+i-1];
        nrw += dof;
        itn=1;                            // 将迭代步置为1
// === 将迭代步位移增量置为0 ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectdu[(idof-1)*(knode)+inod-1] = 0.0;
    }
    else                              // 若不收敛
    {
// === 更新当前迭代步增量 ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectdu[(idof-1)*(knode)+inod-1] = vectue[(idof-1)*(knode)+inod-1];
        itn=itn+1;                        // 更新迭代步
    }
// === 将本迭代步结果存储到指针数组unod中 ===
    n=0;
    n=n+dof;
    n=n+dof;
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            unoda[(nrw+j-1)*knode+i-1] = vectu1[(j-1)*(knode)+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            unoda[(nrw+j-1)*knode+i-1] = vectdu[(j-1)*(knode)+i-1];
    nrw += dof;
    free(vectu1);
    free(vectu);
    free(vectue);
    free(vectdu);
    free(vectgu);
    return;
}
