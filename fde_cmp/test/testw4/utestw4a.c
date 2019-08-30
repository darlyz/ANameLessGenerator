/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = utestw4a.c
Version:2.2
Time of release:2019-08-30 13:09:04
All rights reserved by ECTEC Corporation, and person or
organization using Original software to generated these code,anyone
else must get written permission from ECTEC Corporation to
copy a part or whole of this code.
The Code GenID is:
22565914_000906E9061008007FFAFBFFBFEBFBFF_005056C00001
Copyright is protected from:2017-2030
**************************************************************/
/*
后处理计算程序：
1、解向量扩充，将施加了强制性条件的边界上的自由度扩充到求解器解出来的解向量中；
2、若是非线性问题，则对解进行调整，求出当前迭代步的结果；
3、判断是否收敛，若收敛则迭代标识符end置1。
*/
#include "felac.h"
/* subroutine */
void utestw4a(coor0,dof,nodvar,u,f)
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
    double *vectu;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode*dof;
    vectu = (double *) calloc(kvar,sizeof(double));
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
// 存储求解的u
    free(unoda);
    n=0;
    n=n+dof;
    unoda = (double *) calloc(n*knode,sizeof(double));
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            unoda[(nrw+j-1)*knode+i-1] = vectu[(j-1)*(knode)+i-1];
    nrw += dof;
    free(vectu);
    return;
}
