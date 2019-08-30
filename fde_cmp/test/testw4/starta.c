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
��ʼ������
1���õ����Է�����δ֪���ĸ����Լ�ÿ��δ֪�ڵ��Ӧ�ķ��̺ţ�
2������Ԫ�նȾ����ÿ��Ԫ�أ�����Ԫ�����ܸնȾ���Ԫ�أ�����Ԫ��һһ��Ӧ����Ӧalch()������
3�����ܸնȾ����ÿһ�н������򣬵õ�ÿһ�з���ԪԪ�صĸ�����λ�ã�����
   Ϣ����һά����na��numcol�У���Ӧblch()������
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
    �������ͣ�
    nelem��  �ó�ĳ���͵�Ԫ�ĵ�Ԫ������
    nnode��  ĳ���͵�Ԫһ����Ԫ�ϵĽڵ���+1(��������)��
    neq��    �ó����󷽳�������
    maxcol�� ����նȾ��������кţ�
    maxa:    �ܸշ���Ԫ������
    kvar��   �����ɶ�����
    dim��    ����ά�ȣ�
    knode��  �ڵ�������
    dof��    �ó�ÿ���ڵ�����ɶ�����
    ntype��  �ó���Ԫ��������
    *coor��  �ڵ�����ռ䣻
    *nodvar���ó��ڵ����ɶȶ�Ӧ�Ĺ�������߷��̺ţ�
    *numcol���ܸվ���ÿ��(����)����ʼԪ����na�е�λ�ã�
    *na��    �ܸ�ȥ��Ԫ,һά�����洢����
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
    /*  �������нڵ��ϵ��������ɶȣ��õ�ÿ��δ֪����Ӧ�ķ��̺��Լ�������ķ��̸���neq  */
    for (j = 1; j <= knode; ++j)
    {
        for (i = 1; i <= dof; ++i)
        {
            if (nodvar[(i-1)*(knode)+j-1] == 1)
                nodvar[(i-1)*(knode)+j-1] = ++neq;
        }
    }
    /*  �ӽڵ�δ֪���ķ��̺��ϴ���ڵ������Լ����ϵ  */
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

    /* ��� knode�ĸ�����neq�٣�����ؽڵ�����ͳ�� (status = 1); ������ ������ɶ���ͳ�� (status = 0) */
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
    /*  ����ÿ�����͵����е�Ԫ������Ԫ�նȾ����ÿ��Ԫ�أ�����Ԫ�����ܸնȾ����Ԫ�أ�����Ԫ��һһ��Ӧ  */
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
            /*  ��һ����Ԫ�У�l��ʾ�õ�Ԫ�д��󷽳�����������i���̶�Ӧ�����巽�̺Ÿ���lm[i]  */
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
            /*  aclh�������õ��ܸվ������Ԫ��λ��(�洢��*mht������)��
                         �õ��ܸվ���ÿ�з���Ԫ�ĸ���(�洢��*numcol��)  */
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
    /*  bclh��������mht���������򣬽����еķ���Ԫ�ش洢��na�У�
                  �õ�����նȾ���ÿ�е���ʼԪ����na�е�λ��(�洢��numcol��)  */
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

    /*  �ѵõ�������նȾ�����Ϣ�洢��matrix��ȥ  */
    maxa = numcol[neq];
    (*matrix).maxa = maxa;
    (*matrix).neq = neq;
    (*matrix).na = na;
    (*matrix).a = (double *) calloc(maxa + 1, sizeof(double));
    (*matrix).numcol = numcol;
    (*f) = (double *) calloc(neq + 1, sizeof(double));

    return;
}
