#include "felac.h"
void aec8g2(double *,double *,double *,double *,double *,double *,double *,int,int);
void alq4g2(double *,double *,double *,double *,double *,double *,double *,int,int);
double *unodg;
void adda(int *,double *,int *,int,int *,double *,int,int);
void etesta(coor0,dof,nodvar,ubf,elem,matrix,f)
struct coordinates coor0;
struct element elem;
int dof;
int *nodvar;
double *ubf;
struct matrice matrix;
double *f;
{
    int ntype,nnode,kvar,ibegin;
    int i,j,k,l,m,kk,ij,nn,mm,nr,nrw,ne,nne,numel,idof,jdof,
        inod,jnod,nodi,nodj,inv,jnv;
    int dim,knode,neq;
    int node[500],lm[500];
    double prmt[500],coef[500];
    double *coor,*r,*u;
    int *numcol,maxa,*na;
    double *a,*estifn;
    double mate[500];
    double *es,*em,*ec,*ef;
    double *vectu1,*vectv1,*vectu,*vectdu,*vectuu1;
    double *varw,*varv;
    double aa,bb,ab,rab,err,ul;
    static double cc;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode*dof;
    vectu1 = (double*) calloc (kvar, sizeof(double));
    vectv1 = (double*) calloc (kvar, sizeof(double));
    vectu = (double*) calloc (kvar, sizeof(double));
    vectdu = (double*) calloc (kvar, sizeof(double));
    vectuu1 = (double*) calloc (kvar, sizeof(double));
    varw = (double*) calloc (knode+1, sizeof(double));
    varv = (double*) calloc (knode+1, sizeof(double));
    a = matrix.a;
    na = matrix.na;
    neq = matrix.neq;
    maxa = matrix.maxa;
    numcol = matrix.numcol;
    for (i=1; i<=maxa; ++i)
        a[i] = 0.0;
    u = (double *) calloc(kvar,sizeof(double));
    r = (double *) calloc(500,sizeof(double));
    for (i=0; i<kvar; ++i)
        u[i] = ubf[i];
    nrw = 0;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            u1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            v1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            u[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            du[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            uu1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    nn = 0;
    mm = 0;
    numel = 0;
    ntype = elem.ntype;
    for (ityp=1; ityp<=ntype; ++ityp)
    {
        ibegin=1;
        nmate = elem.nmate[ityp];
        nprmt = elem.nprmt[ityp];
        for (i=1; i<=nmate; ++i)
            for(j=1; j<=nprmt; ++j)
                mate[(i-1)*nprmt+j] = elem.mate[++mm];
        nelem = elem.nelem[ityp];
        nnode = elem.nnode[ityp];
        nne   = nnode-1;
        for(ne=1; ne<=nelem; ++ne)
        {
            for (j=1; j<=nnode; ++j)
                node[j] = elem.node[++nn];
            if(node[nnode]<0)
            {
                if(ne==ibegin)ibegin=ibegin+1;
                goto l700;
            }
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
                ef = (double *) calloc(k+1,sizeof(double));
            }
            for (j=1; j<=nne; ++j)
            {
                jnod=node[j];
                if(jnod<0)
                    jnod = -jnod;
                prmt[nprmt+j] = jnod;
                i = 0;
                for (l=1; l<=dof; ++l)
                {
                    coef[j-1+i*nne]=vectuu1[(l-1)*(knode)+jnod-1];
                    i++;
                }
                coef[j-1+i*nne]=varw[jnod];
                i++;
                coef[j-1+i*nne]=varv[jnod];
                i++;
                for(i=1; i<=dim; ++i)
                    r[(i-1)*(nne)+j-1] = coor[(i-1)*(knode)+jnod-1];
            }
            imate = node[nnode];
            for (j=1; j<=nprmt; ++j)
                prmt[j] = mate[(imate-1)*nprmt+j];
            switch (ityp)
            {
            case 1 :
                aec8g2(r,coef,prmt,es,em,ec,ef,ne,ibegin);
                break;
            case 2 :
                alq4g2(r,coef,prmt,es,em,ec,ef,ne,ibegin);
                break;
            }
            for (i=1; i<=k; ++i)
                for (j=1; j<=k; ++j)
                    estifn[(i-1)*(k)+j-1]=0.0;
            for (i=1; i<=k; ++i)
            {
                for (j=1; j<=k; ++j)
                {
                    estifn[(i-1)*(k)+j-1]=estifn[(i-1)*(k)+j-1]
                                         +es[(i-1)*(k)+j-1]*dt*dt/4;
                }
                estifn[(i-1)*(k)+i-1]=estifn[(i-1)*(k)+i-1]
                                     +em[i]
                                     +ec[i]*dt/2;
            }
            i=0;
            for (inod=1; inod<=nne; ++inod)
            {
                nodi = node[inod];
                for (idof=1; idof<=dof; ++idof)
                {
                    inv = nodvar[(idof-1)*(knode)+nodi-1];
                    if (inv==0)
                        goto l600;
                    i++;
                    lm[i] = inv;
                    if  (inv>0)
                    {
                        u[(idof-1)*(knode)+nodi-1] = u[(idof-1)*(knode)+nodi-1]
                                                   +ef[i]*dt*dt/2
                                                   +em[i]*vectu1[(idof-1)*(knode)+nodi-1]
                                                   +em[i]*vectv1[(idof-1)*(knode)+nodi-1]*dt
                                                   +ec[i]*vectu1[(idof-1)*(knode)+nodi-1]*dt/2;
                    }
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
                                                           -es[(i-1)*(k)+j-1]*vectu1[(idof-1)*(knode)+nodi-1]*dt*dt/4
                                                           +es[(i-1)*(k)+j-1]*vectu[(idof-1)*(knode)+nodi-1]*dt*dt/2;
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
    free(vectv1);
    free(vectu);
    free(vectdu);
    free(vectuu1);
    free(varw);
    free(varv);
    return;
}
