/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = epgsub.c
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
#include <stddef.h>
#include<stdlib.h>
#include <stdio.h>
/* aclh函数：将单元刚度矩阵的每个元素（非零元）与总刚度矩阵元素（非零元）一一对应，存储在mht中
             得到总刚矩阵每行非零元的个数，存储在numcol中 */
void aclh(numcol,nap,naj,nd,lm,jna,numcolum)
int *numcol,***nap,***naj;
int nd;
int *lm;
int *jna;
int numcolum;
{
    int i,j,k,jj,ni,nj,numj,jp,jv;
    for(i=1; i<=nd; i++)
    {
        ni = lm[i];
        for(j=1; j<=nd; j++)
        {
            nj=lm[j];
            numj=numcol[ni];
            if(numj==0)
            {
                *jna=*jna+1;
                if((*nap)[(ni-1)/numcolum]==NULL)
                {
                    (*nap)[(ni-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    (*naj)[(ni-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    for(jj=0; jj<numcolum; jj++)
                    {
                        (*nap)[(ni-1)/numcolum][jj]=0;
                        (*naj)[(ni-1)/numcolum][jj]=0;
                    }
                }
                (*nap)[(ni-1)/numcolum][(ni-1)%numcolum]=*jna;
                (*naj)[(ni-1)/numcolum][(ni-1)%numcolum]=nj;

                numcol[ni]=numcol[ni]+1;
            }
            else
            {
                if((*nap)[(ni-1)/numcolum]==NULL)
                {
                    (*nap)[(ni-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    (*naj)[(ni-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    for(jj=0; jj<numcolum; jj++)
                    {
                        (*nap)[(ni-1)/numcolum][jj]=0;
                        (*naj)[(ni-1)/numcolum][jj]=0;
                    }
                }
                jp=(*nap)[(ni-1)/numcolum][(ni-1)%numcolum];
                jv=(*naj)[(ni-1)/numcolum][(ni-1)%numcolum];
                if(nj==jv)goto l300;
                for(k=0; k<(numj-1); k++)
                {
                    if((*nap)[(jp-1)/numcolum]==NULL)
                    {
                        (*nap)[(jp-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                        (*naj)[(jp-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                        for(jj=0; jj<numcolum; jj++)
                        {
                            (*nap)[(jp-1)/numcolum][jj]=0;
                            (*naj)[(jp-1)/numcolum][jj]=0;
                        }
                    }
                    jv=(*naj)[(jp-1)/numcolum][(jp-1)%numcolum];
                    jp=(*nap)[(jp-1)/numcolum][(jp-1)%numcolum];
                    if(nj==jv) goto l300;
                }
                *jna=*jna+1;
                if((*nap)[(jp-1)/numcolum]==NULL)
                {
                    (*nap)[(jp-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    (*naj)[(jp-1)/numcolum] =(int *)calloc(numcolum,sizeof(int));
                    for(jj=0; jj<numcolum; jj++)
                    {
                        (*nap)[(jp-1)/numcolum][jj]=0;
                        (*naj)[(jp-1)/numcolum][jj]=0;
                    }
                }
                (*nap)[(jp-1)/numcolum][(jp-1)%numcolum]=*jna;
                (*naj)[(jp-1)/numcolum][(jp-1)%numcolum]=nj;
                numcol[ni]=numcol[ni]+1;

            }
l300:
            continue;
        }
    }
    return;
}

/* bclh函数：对mht矩阵按行排序，将其中的非零元素存储在na中；
             得到总体刚度矩阵每行的起始元素在na中的位置(存储在numcol中) */
/*subroutine*/ void bclh(knode,nap,naj,numcol,na,jdiag,nodvar,lmi,numcolum,neq,maxa,dof,status)
int knode,**nap,**naj,*numcol,*na,*jdiag,*nodvar,*lmi,numcolum,neq,maxa,dof,status;
{
    void order(int,int *);
    int n,nn,ij,ik,colnum,i,jp,jv,li,nsum,j,k,minnum;
    int *numcoltmp;

    numcoltmp = (int *) calloc(neq+1,sizeof(int));

    for(i=0; i<neq+1; i++)
        numcoltmp[i]=0;
    nn=1;
    minnum=neq;
    if(status==1)
    {
        for(n=0; n<knode; n++)
        {
            numcol[neq-n]=numcol[knode-n];
        }
        minnum=knode;
    }
    for(n=0; n<minnum; n++)
    {
        if(status==1)
        {
            ik=neq-knode+n+1;
            li=numcol[ik];
        }
        else
            li=numcol[n+1];

        jp=nap[n/numcolum][n%numcolum];
        jv=naj[n/numcolum][n%numcolum];
        for(i=1; i<=li; i++)
        {
            lmi[i]=jv;
            jv=naj[(jp-1)/numcolum][(jp-1)%numcolum];
            jp=nap[(jp-1)/numcolum][(jp-1)%numcolum];
        }
        order(li,lmi);
        if(status==1)
        {
            colnum=0;
            for(i=1; i<=li; i++)
            {
                for(j=0; j<dof; j++)
                {
                    if(nodvar[j*knode+lmi[i]-1]>0)
                    {
                        colnum=colnum+1;
                    }
                }
            }
            for(j=0; j<dof; j++)
            {
                if(nodvar[j*knode+n]>0)
                {
                    numcoltmp[nodvar[j*knode+n]]=colnum;
                }
            }
            for(ij=0; ij<dof; ij++)
            {
                if(nodvar[ij*knode+n]>0)
                {
                    for(i=1; i<=li; i++)
                    {
                        for(j=0; j<dof; j++)
                        {
                            if(nodvar[j*knode+lmi[i]-1]>0)
                            {
                                na[nn]=nodvar[j*knode+lmi[i]-1];
                                nn=nn+1;
                            }
                        }
                    }
                }
            }
        }
        else
        {
            for(i=1; i<=li; i++)
            {
                na[nn]=lmi[i];
                nn=nn+1;
            }
        }

    }
    if (status == 1)
    {
        for(n=0; n<neq+1; n++)
        {
            numcol[n]=numcoltmp[n];
        }
    }
    free(numcoltmp);

    for (n=1; n<=neq; ++n)
    {
        numcol[n] += numcol[n-1];
    }

    for (i=0; i<neq; i++)
    {
        for (j=numcol[i]; j<numcol[i+1]; j++)
        {
            if(na[j+1]==(i+1)) goto l200;
        }
l200:
        jdiag[i]=j+1;
    }

    return;
}

/* order:排序函数，从小到大排序 */
/*subroutine*/ void order(nd,lm)
int nd,*lm;
{
    int i,j,j0,ls;
    for (i=1; i<=nd; ++i)
    {
        ls = lm[i]+1;
        for (j=i; j<=nd; ++j)
        {
            if (lm[j]<=ls)
            {
                ls = lm[j];
                j0 = j;
            }
        }
        lm[j0] = lm[i];
        lm[i]  = ls;
    }
    return;
}

void chms(dof,knode,nodvar,ubf)
int dof,knode,*nodvar;
double *ubf;
{
    int is[1000],ms[1000];
    int m,j0,k,i,j,ii;
    for (j=1; j<=dof; ++j)
    {
        m=0;
        for (i=1; i<=knode; ++i)
        {
            if (nodvar[(j-1)*(knode)+i-1] > 1)
            {
                k=nodvar[(j-1)*(knode)+i-1];
                j0=0;
                if(m>0)
                {
                    for(ii=1; ii<=m; ++ii)
                    {
                        if(k==ms[ii])
                            j0=is[ii];
                    }
                }
                if(j0==0)
                {
                    m=m+1;
                    ms[m]=k;
                    is[m]=i;
                    nodvar[(j-1)*(knode)+i-1]=1;
                }
                else
                {
                    nodvar[(j-1)*(knode)+i-1]=-j0-1;
                    ubf[(j-1)*(knode)+i-1]=0.0;
                }
            }
        }
    }
    return;
}


