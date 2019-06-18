/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = echeck3a.c
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
��Ԫ�������
1��ѭ��ȫ���ĵ�Ԫ���͵����е�Ԫ������ÿ����Ԫ�ĵ��ա����ʡ����衢��Ԫ�غ�������
2�����ɵ�Ԫ���ɶȱ�ʾ�ĸ���������Ϊ���������ɶ���������Ӧ���������
3������ǿ��Լ��������
*/
#include "felac.h"
void aec8g2(double *,double *,double *,double *,double *,double *,double *,int,int);
double *unodg;
/*  adda��������������նȾ���  */
void adda(int *,double *,int *,int,int *,double *,int,int);
void echeck3a(coor0,dof,nodvar,ubf,elem,matrix,f)
int dof,*nodvar;
double *ubf,*f;
struct coordinates coor0;
struct element elem;
struct matrice matrix;
{
    /*�������ͣ�
    dof��    �ó�ÿ���ڵ�����ɶ�����
    ntype��  �ó���Ԫ��������
    nnode:   ĳ���͵�Ԫһ����Ԫ�ϵĽڵ���+1(��������)��
    kvar:    �����ɶ�����
    nne��    ĳ���͵�Ԫһ����Ԫ�ϵĽڵ�����
    dim��    ����ά����
    knode��  �ڵ�������
    neq��    �ó����󷽳�������
    maxa��   �ó��ܸվ���Ԫ��������
    ubf��    �߽�ֵ��
    nmate��  ĳ�ֵ�Ԫ���Ͷ�Ӧ�Ĳ�������
    nprmt��  ĳ�����͵�Ԫ���϶�Ӧ�Ĳ��ϲ���������
    nelem��  �ó�ĳ���͵�Ԫ�ĵ�Ԫ������
    mate[]�� ���ϲ���ֵ�ռ䣻
    prmt[]:  ǰnprmt��Ԫ�ش洢��Ԫ�Ĳ�����Ϣ����nne��Ԫ�ش洢��Ԫ������ڵ�ţ�
    coef[]:  ��ϳ���Ϣ��
    node[]�� ���е�Ԫ�ĵ�Ԫ���˹�ϵ�ռ䣻
    lm[]:    ��Ԫ������δ֪�����̺ſռ䣻
    *nodvar���ó��ڵ����ɶȶ�Ӧ�Ĺ�������߷��̺ţ�
    *numcol������նȾ���ÿ��(����)����ʼԪ����na�е�λ�ã�
    *coor��  �ڵ�����ռ䣻
    *r:      ��Ԫ�ڵ�����ռ�
    *a��     �ܸվ���
    *na��    �ܸ�ȥ��Ԫ һά�����洢����
    *es��    ��Ԫ�նȾ���
    *em��    ��Ԫ��������
    *ec��    ��Ԫ�������
    *ef��    ��Ԫ����������
    */
    int ntype,nnode,kvar,ibegin;
    int i,j,k,l,m,kk,ij,nn,mm,nr,nrw,ne,nne,numel,idof,jdof,
        inod,jnod,nodi,nodj,inv,jnv;
    int dim,knode,neq,*numcol,maxa,*na,node[500],lm[500];
    double *a,mate[500],prmt[500],coef[500],*u;
    double *coor,*r;
    double *estifn;
    double *es,*em,*ec,*ef;
    double *vectu1,*vectdu;
    double aa,bb,ab,rab,err,ul;
    static double cc;
    es = null;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode*dof;
    vectu1 = (double *) calloc(kvar,sizeof(double));
    vectdu = (double *) calloc(kvar,sizeof(double));
    a = matrix.a;
    na = matrix.na;
    neq = matrix.neq;
    maxa = matrix.maxa;
    numcol = matrix.numcol;
    for(i=1; i<=maxa; ++i)
    {
        a[i] = 0.0;
    }
    u = (double *) calloc(kvar,sizeof(double));
    r = (double *) calloc(500,sizeof(double));
    for(i=0; i<kvar; ++i)
    {
        u[i]=ubf[i];
    }
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectu1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectdu[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    numel = 0;
    nn = 0;
    mm = 0;
    ntype = elem.ntype;
    /*  ��������նȾ����Լ��߽紦��  */
    for (ityp=1; ityp<=ntype; ++ityp)
    {
        ibegin=1;
        nmate = elem.nmate[ityp];
        nprmt = elem.nprmt[ityp];
        /*  �õ�ĳ���͵�Ԫ��ĳ���ϵĲ��ϲ���ֵ���洢��mate��  */
        for (i=1; i<=nmate; ++i)
            for(j=1; j<=nprmt; ++j)
                mate[(i-1)*nprmt+j] = elem.mate[++mm];
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne   = nnode-1;
        for(ne=1; ne<=nelem; ++ne)
        {
            /*  ��ȡ��Ԫ�ڵ����˹�ϵ���洢��node��  */
            for (j=1; j<=nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)
            {
                if(ne==ibegin)ibegin=ibegin+1;
                goto l700;
            }
            /*  ͨ��ÿ�����͵�Ԫ�ĵ�һ����Ԫ�����ɶȹ����ȷ�������͵�Ԫ�ĵ��գ����ʵȾ����С  */
            if  (ne==ibegin)
            {
                k=0;
                for(j=1; j<=nne; ++j)
                {
                    jnod = node[j];
                    if(jnod>0)
                        for(l=1; l<=dof; ++l)
                            if(nodvar[(l-1)*(knode)+jnod-1] !=0 )
                                k++;
                }
                kk = k*k;
                es = (double *) calloc(kk,sizeof(double));
                em = (double *) calloc(k+1,sizeof(double));
                ec = (double *) calloc(k+1,sizeof(double));
                ef = (double *) calloc(k+1,sizeof(double));
                estifn = (double *) calloc(kk+1,sizeof(double));
            }
            /*  ��ȡ��Ԫ��Ϣ����Ԫ������ڵ��(�洢��prmt��)����Ԫ�ڵ�����(�洢��r��)  */
            for (j=1; j<=nne; ++j)
            {
                jnod=node[j];
                if(jnod<0)
                    jnod = -jnod;
                prmt[nprmt+j] = jnod;
                i=0;
                for (l=1; l<=dof; ++l)
                {
                    coef[j-1+i*nne]=vectu1[(l-1)*(knode)+jnod-1];
                    i++;
                }
                for(i=1; i<=dim; ++i)
                    r[(i-1)*(nne)+j-1] = coor[(i-1)*(knode)+jnod-1];
            }
            /*  ��ȡ��Ԫ��Ϣ����Ԫ�Ĳ�����Ϣ(�洢��prmt��)  */
            imate = node[nnode];
            for (j=1; j<=nprmt; ++j)
                prmt[j] = mate[(imate-1)*nprmt+j];
            /*  ���õ�Ԫ�ӳ��򣬼��㵥Ԫ�նȾ���,��Ԫ��������,��Ԫ�������͵�Ԫ�غ�����  */
            switch (ityp)
            {
            case 1 :
                aec8g2(r,coef,prmt,es,em,ec,ef,ne,ibegin);
                break;
            }
            /*  ��ϵ�Ԫ�նȾ��󡢵�Ԫ�������󡢵�Ԫ�������õ���Ԫ���󣬶�Ӧsch�㷨�ļ��е�matrix��  */
            for (i=1; i<=k; ++i)
                for (j=1; j<=k; ++j)
                    estifn[(i-1)*(k)+j-1]=0.0;
            for (i=1; i<=k; ++i)
            {
                for (j=1; j<=k; ++j)
                {
                    estifn[(i-1)*(k)+j-1]=estifn[(i-1)*(k)+j-1]
                                          +es[(i-1)*(k)+j-1];
                }
                estifn[(i-1)*(k)+i-1]=estifn[(i-1)*(k)+i-1]
                                      ;
            }
            i=0;
            /*  ����߽��������õ���Ԫ�����Ҷ���  */
            for (inod=1; inod<=nne; ++inod)
            {
                nodi = node[inod];
                for (idof=1; idof<=dof; ++idof)
                {
                    inv = nodvar[(idof-1)*(knode)+nodi-1];
                    if (inv==0)
                        goto l600;
                    /*  i�м�¼inv(�����)������0�����ɶ���Ŀ  */
                    i++;
                    /*  lm�м�¼inv(�����)������0��ÿ���ڵ��ÿ�����ɶȶ�Ӧ�ķ��̺�  */
                    lm[i] = inv;
                    /*  �������ɶȹ����������ķ��̣����к��ش�����Ӧsch�㷨�ļ��е�force��  */
                    if  (inv>0)
                    {
                        u[(idof-1)*(knode)+nodi-1] = u[(idof-1)*(knode)+nodi-1]
                                                     +ef[i];
                    }
                    /*  ����ǿ�Ʊ߽�����  */
                    j = 0;
                    for (jnod=1; jnod<=nne; ++jnod)
                    {
                        nodj = node[jnod];
                        for(jdof=1; jdof<=dof; ++jdof)
                        {
                            jnv = nodvar[(jdof-1)*(knode)+nodj-1];
                            if (jnv==0)
                                goto l400;
                            j++;
                            if(jnv>0)
                            {
                                u[(jdof-1)*(knode)+nodj-1] = u[(jdof-1)*(knode)+nodj-1]
                                                             +es[(i-1)*(k)+j-1]*vectu1[(idof-1)*(knode)+nodi-1];
                                /*  ����ǿ�Ʊ߽��������������ɶ�δ֪����Щ�У����Ҷ���Ҫ��ȥ���з�������֪���ɶ���ص���  */
                                if  (inv<0)
                                    u[(jdof-1)*(knode)+nodj-1]=u[(jdof-1)*(knode)+nodj-1]-estifn[(i-1)*(k)+j-1]*u[(idof-1)*(knode)+nodi-1];
                            }
l400:
                            continue;
                        }
                    }
l600:
                    continue;
                }
            }
            /*  ��������նȾ���  */
            adda(na,a,numcol,k,lm,estifn,neq,maxa);
l700:
            if(ne==nelem)
            {
                if(es != null)
                {
                    free(es);
                    free(em);
                    free(ec);
                    free(ef);
                    free(estifn);
                }
            }
        }
        numel += nelem;
    }
    free(r);
    /*  ���ݵ�Ԫѭ���еõ���u���õ����巽���Ҷ����Ϊһά�洢(�洢������f��)  */
    for (ij=1; ij<=neq; ++ij)
    {
        f[ij] = 0.0;
    }
    for (i=1; i<=dof; ++i)
    {
        for (j=1; j<=knode; ++j)
        {
            ij = nodvar[(i-1)*(knode)+j-1];
            if  (ij>0)
                f[ij] += u[(i-1)*(knode)+j-1];
        }
    }
    free(u);
    free(vectu1);
    free(vectdu);
    return;
}
