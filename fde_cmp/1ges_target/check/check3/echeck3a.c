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
单元计算程序：
1、循环全部的单元类型的所有单元，计算每个单元的单刚、单质、单阻、单元载荷向量；
2、将由单元自由度表示的各矩阵扩充为由整体自由度列向量对应的总体矩阵；
3、处理强制约束条件。
*/
#include "felac.h"
void aec8g2(double *,double *,double *,double *,double *,double *,double *,int,int);
double *unodg;
/*  adda函数：集成总体刚度矩阵  */
void adda(int *,double *,int *,int,int *,double *,int,int);
void echeck3a(coor0,dof,nodvar,ubf,elem,matrix,f)
int dof,*nodvar;
double *ubf,*f;
struct coordinates coor0;
struct element elem;
struct matrice matrix;
{
    /*变量解释：
    dof：    该场每个节点的自由度数；
    ntype：  该场单元类型数；
    nnode:   某类型单元一个单元上的节点数+1(包括材料)；
    kvar:    总自由度数；
    nne：    某类型单元一个单元上的节点数；
    dim：    坐标维数；
    knode：  节点总数；
    neq：    该场待求方程总数；
    maxa：   该场总刚矩阵元素总数；
    ubf：    边界值；
    nmate：  某种单元类型对应的材料数；
    nprmt：  某种类型单元材料对应的材料参数个数；
    nelem：  该场某类型单元的单元总数；
    mate[]： 材料参数值空间；
    prmt[]:  前nprmt个元素存储单元的材料信息，后nne个元素存储单元的整体节点号；
    coef[]:  耦合场信息；
    node[]： 所有单元的单元拓扑关系空间；
    lm[]:    单元中所有未知量方程号空间；
    *nodvar：该场节点自由度对应的规格数或者方程号；
    *numcol：总体刚度矩阵每行(或列)的起始元素在na中的位置；
    *coor：  节点坐标空间；
    *r:      单元节点坐标空间
    *a：     总刚矩阵；
    *na：    总刚去零元 一维变带宽存储矩阵；
    *es：    单元刚度矩阵；
    *em：    单元质量矩阵；
    *ec：    单元阻尼矩阵；
    *ef：    单元荷载向量。
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
    /*  计算总体刚度矩阵以及边界处理  */
    for (ityp=1; ityp<=ntype; ++ityp)
    {
        ibegin=1;
        nmate = elem.nmate[ityp];
        nprmt = elem.nprmt[ityp];
        /*  得到某类型单元的某材料的材料参数值，存储在mate中  */
        for (i=1; i<=nmate; ++i)
            for(j=1; j<=nprmt; ++j)
                mate[(i-1)*nprmt+j] = elem.mate[++mm];
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne   = nnode-1;
        for(ne=1; ne<=nelem; ++ne)
        {
            /*  读取单元节点拓扑关系，存储在node中  */
            for (j=1; j<=nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)
            {
                if(ne==ibegin)ibegin=ibegin+1;
                goto l700;
            }
            /*  通过每个类型单元的第一个单元的自由度规格数确定该类型单元的单刚，单质等矩阵大小  */
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
            /*  读取单元信息：单元的整体节点号(存储在prmt中)，单元节点坐标(存储在r中)  */
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
            /*  读取单元信息：单元的材料信息(存储在prmt中)  */
            imate = node[nnode];
            for (j=1; j<=nprmt; ++j)
                prmt[j] = mate[(imate-1)*nprmt+j];
            /*  调用单元子程序，计算单元刚度矩阵,单元质量矩阵,单元阻尼矩阵和单元载荷向量  */
            switch (ityp)
            {
            case 1 :
                aec8g2(r,coef,prmt,es,em,ec,ef,ne,ibegin);
                break;
            }
            /*  组合单元刚度矩阵、单元质量矩阵、单元阻尼矩阵得到单元矩阵，对应sch算法文件中的matrix行  */
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
            /*  处理边界条件，得到单元矩阵右端项  */
            for (inod=1; inod<=nne; ++inod)
            {
                nodi = node[inod];
                for (idof=1; idof<=dof; ++idof)
                {
                    inv = nodvar[(idof-1)*(knode)+nodi-1];
                    if (inv==0)
                        goto l600;
                    /*  i中记录inv(规格数)不等于0的自由度数目  */
                    i++;
                    /*  lm中记录inv(规格数)不等于0的每个节点的每个自由度对应的方程号  */
                    lm[i] = inv;
                    /*  对于自由度规格数大于零的方程，进行荷载处理，对应sch算法文件中的force项  */
                    if  (inv>0)
                    {
                        u[(idof-1)*(knode)+nodi-1] = u[(idof-1)*(knode)+nodi-1]
                                                     +ef[i];
                    }
                    /*  处理强制边界条件  */
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
                                /*  处理强制边界条件，对于自由度未知的那些行，其右端项要减去该行方程与已知自由度相关的项  */
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
            /*  集成总体刚度矩阵  */
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
    /*  根据单元循环中得到的u，得到总体方程右端项并改为一维存储(存储在数组f中)  */
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
