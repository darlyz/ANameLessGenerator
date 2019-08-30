/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = starta.c
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
初始化程序：
1、得到线性方程组未知量的个数以及每个未知节点对应的方程号；
2、将单元刚度矩阵的每个元素（非零元）与总刚度矩阵元素（非零元）一一对应，对应alch()函数；
3、对总刚度矩阵的每一行进行排序，得到每一行非零元元素的个数与位置，将信
   息存在一维数组na和numcol中，对应blch()函数。
*/
#include "felac.h"

void order(int, int *);
int aclh(int *, int ***, int ***, int, int *, int *, int);
void bclh(int, int **, int **, int *, int *, int *, int *, int *, int, int, int, int, int);
void chms(int,int,int *,double *);
/* subroutine */
void starta(coor0, dof, nodvar, ubf,elem, matrix, f)
int dof, *nodvar;
double **f,*ubf;
struct coordinates coor0;
struct element elem;
struct matrice *matrix;
{
    /*
    变量解释：
    nelem：  该场某类型单元的单元总数；
    nnode：  某类型单元一个单元上的节点数+1(包括材料)。
    neq：    该场待求方程总数；
    maxcol： 总体刚度矩阵的最大列号；
    maxa:    总刚非零元总数；
    kvar：   总自由度数；
    dim：    坐标维度；
    knode：  节点总数；
    dof：    该场每个节点的自由度数；
    ntype：  该场单元类型数；
    *coor：  节点坐标空间；
    *nodvar：该场节点自由度对应的规格数或者方程号；
    *numcol：总刚矩阵每行(或列)的起始元素在na中的位置；
    *na：    总刚去零元,一维变带宽存储矩阵；
    */
    int nelem, nnode, neq, jna;
    int *numcol, *na, **nap, **naj;
    int i, j, l, n, nn, ne, nne, inod, nodi, numel, idof, ityp, inv, maxa, kvar, numrow, numcolum, status,slavenode;
    int lm[500], node[500];
    int dim, knode;
    double *coor;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode * dof;
    neq = 0;
    numrow = 200;
    numcolum = 5000000;
    status = 0;
    slavenode=0;

    for (j = 1; j <= knode; ++j)
    {
        for (i = 1; i <= dof; ++i)
        {
            if (nodvar[(i-1)*(knode)+j-1] == 0)
            {
                nodvar[(i-1)*(knode)+j-1] = -10;
            }
            else if(nodvar[(i-1)*(knode)+j-1] == 1)
            {
                nodvar[(i-1)*(knode)+j-1] = 0;
            }
            else if(nodvar[(i-1)*(knode)+j-1] > 1)
            {
                slavenode=slavenode+1;
            }
        }
    }
    nn = 0;
    for (ityp = 1; ityp <= elem.ntype; ++ityp)
    {
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne = nnode - 1;
        for (i = 1; i <= nelem; ++i)
        {
            for (j = 1; j <= nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)continue;
            for (inod = 1; inod <= nne; ++inod)
            {
                nodi = node[inod];
                for (idof = 1; idof <= dof; ++idof)
                {
                    if(nodvar[(idof-1)*(knode)+nodi-1]==0)nodvar[(idof-1)*(knode)+nodi-1]=1;
                }
            }
        }
    }
    nn = 0;
    for (ityp = 1; ityp <= elem.ntype; ++ityp)
    {
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne = nnode - 1;
        for (i = 1; i <= nelem; ++i)
        {
            for (j = 1; j <= nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)continue;
            for (inod = 1; inod <= nne; ++inod)
            {
                nodi = node[inod];
                for (idof = 1; idof <= dof; ++idof)
                {
                    if(nodvar[(idof-1)*(knode)+nodi-1]<-1)nodvar[(idof-1)*(knode)+nodi-1]=0;
                }
            }
        }
    }

    chms(dof,knode,nodvar,ubf);
    /*  遍历所有节点上的所有自由度，得到每个未知量对应的方程号以及方程组的方程个数neq  */
    for (j = 1; j <= knode; ++j)
    {
        for (i = 1; i <= dof; ++i)
        {
            if (nodvar[(i-1)*(knode)+j-1] == 1)
                nodvar[(i-1)*(knode)+j-1] = ++neq;
        }
    }
    /*  从节点未知量的方程号上处理节点的主从约束关系  */
    for (j = 1; j <= knode; ++j)
    {
        for (i = 1; i <= dof; ++i)
        {
            if (nodvar[(i-1)*(knode)+j-1] < -1)
            {
                n = -nodvar[(i-1)*(knode)+j-1] - 1;
                nodvar[(i-1)*(knode)+j-1] = nodvar[(i-1)*(knode)+n-1];
            }
        }
    }

    /* 如果 knode的个数比neq少，则按相关节点数来统计 (status = 1); 否则按照 相关自由度来统计 (status = 0) */
    if(neq > knode) status = 1;
    if(slavenode>1) status = 0;
    (*matrix).jdiag = (int *) calloc(neq, sizeof(int));
    numcol = (int *) calloc(neq + 1, sizeof(int));
    for (i = 0; i <= neq; ++i)
        numcol[i] = 0;
    nap = (int **)calloc(numrow, sizeof(int *));
    naj = (int **)calloc(numrow, sizeof(int *));
    nap[0] = (int *)calloc(numcolum, sizeof(int));
    naj[0] = (int *)calloc(numcolum, sizeof(int));
    for(int j = 0; j < numcolum; j++)
    {
        nap[0][j] = 0;
        naj[0][j] = 0;
    }
    for(int j = 1; j < numrow; j++)
    {
        nap[j] = null;
        naj[j] = null;
    }
    if(status == 1)
    {
        jna = knode;
    }
    else
    {
        jna = neq;
    }

    numel = 0;
    nn = 0;
    /*  遍历每种类型的所有单元，将单元刚度矩阵的每个元素（非零元）与总刚度矩阵的元素（非零元）一一对应  */
    for (ityp = 1; ityp <= elem.ntype; ++ityp)
    {
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne = nnode - 1;
        for (i = 1; i <= nelem; ++i)
        {
            for (j = 1; j <= nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)continue;

            l = 0;
            /*  在一个单元中，l表示该单元中待求方程数，并将第i方程对应的整体方程号赋给lm[i]  */
            for (inod = 1; inod <= nne; ++inod)
            {
                nodi = node[inod];
                if(status == 1)
                {
                    l++;
                    lm[l] = nodi;
                }
                else
                {
                    for (idof = 1; idof <= dof; ++idof)
                    {
                        inv = nodvar[(idof-1)*(knode)+nodi-1];
                        if (inv > 0)
                        {
                            l++;
                            lm[l] = inv;
                        }
                    }
                }
            }
            numel++;
            /*  aclh函数：得到总刚矩阵非零元的位置(存储在*mht矩阵中)；
                         得到总刚矩阵每行非零元的个数(存储在*numcol中)  */
            if (l > 0)
                aclh(numcol, &nap, &naj, l, lm, &jna, numcolum);
        }
    }

    maxa = 0;
    if(status == 1)
    {
        for(int ii = 1; ii < knode + 1; ii++)
        {
            maxa = maxa + numcol[ii];
        }
        maxa = maxa * dof * dof + 2;
    }
    else
    {
        for(int ii = 1; ii < neq + 1; ii++)
        {
            maxa = maxa + numcol[ii];
        }
        maxa = maxa + 2;
    }
    na = (int *)calloc(maxa, sizeof(int));
    /*  bclh函数：对mht矩阵按行排序，将其中的非零元素存储在na中；
                  得到总体刚度矩阵每行的起始元素在na中的位置(存储在numcol中)  */
    bclh(knode, nap, naj, numcol, na, (*matrix).jdiag, nodvar, lm, numcolum, neq, maxa, dof, status);

    i=0;
    while (nap[i] != null)
    {
        free( nap[i] );
        free( naj[i] );
        ++i;
    }
    free(nap);
    free( naj );

    /*  把得到的总体刚度矩阵信息存储到matrix中去  */
    maxa = numcol[neq];
    (*matrix).maxa = maxa;
    (*matrix).neq = neq;
    (*matrix).na = na;
    (*matrix).a = (double *) calloc(maxa + 1, sizeof(double));
    (*matrix).numcol = numcol;
    (*f) = (double *) calloc(neq + 1, sizeof(double));

    return;
}
