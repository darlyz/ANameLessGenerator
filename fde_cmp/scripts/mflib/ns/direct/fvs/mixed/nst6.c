extern void nsxyt(double *,double *,double *,double *,double *,double *,double *,int);
void nst6(gcoorr,gcoefr,prmt,gestif,gemass,gedamp,geload,num)
double gcoorr[12],gcoefr[12],*prmt,gestif[225];
double *gemass,*gedamp,*geload;
int num;
{
    double coorr[6],coefr[6],estif[81];
    double emass[100],edamp[100],eload[100];
    int n,i,j,ki,kj,gi,gj,gki,gkj,nnode,gnnode,dim,dof,idof,jdof;
    int nelem,node[12];
    nnode = 3;
    gnnode = 6;
    dof = 3;
    dim = 2;
    nelem = 4;
    node[(1-1)*3+1-1]=1;
    node[(1-1)*3+2-1]=4;
    node[(1-1)*3+3-1]=6;
    node[(2-1)*3+1-1]=4;
    node[(2-1)*3+2-1]=2;
    node[(2-1)*3+3-1]=5;
    node[(3-1)*3+1-1]=6;
    node[(3-1)*3+2-1]=5;
    node[(3-1)*3+3-1]=3;
    node[(4-1)*3+1-1]=4;
    node[(4-1)*3+2-1]=5;
    node[(4-1)*3+3-1]=6;
    for (i=1; i<=15; ++i)
    {
        gemass[i]=0.0;
        gedamp[i]=0.0;
        geload[i]=0.0;
        for (j=1; j<=15; ++j)
        {
            gestif[(i-1)*15+j-1]=0.0;
        }
    }
    for (n=1; n<=nelem; ++n)
    {
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*3+i-1];
            for (idof=1; idof<=dim; ++idof)
            {
                coorr[(idof-1)*3+i-1]=gcoorr[(idof-1)*6+gi-1];
                coefr[(idof-1)*3+i-1]=gcoefr[(idof-1)*6+gi-1];
            }
        }
        nsxyt(coorr,coefr,prmt,estif,emass,edamp,eload,num);
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*3+i-1];
            for (idof=1; idof<=dof-1; ++idof)
            {
                ki = (i-1)*dof+idof;
                gki = (dof-1)*(gi-1)+idof;
                if (gi-1<=nnode) gki=gki+gi-1;
                else gki=gki+nnode;
                gemass[gki]=gemass[gki]+emass[ki];
                gedamp[gki]=gedamp[gki]+edamp[ki];
                geload[gki]=geload[gki]+eload[ki];
                for (j=1; j<=nnode; ++j)
                {
                    gj = node[(n-1)*3+j-1];
                    for (jdof=1; jdof<=dof-1; ++jdof)
                    {
                        kj = (j-1)*dof+jdof;
                        gkj = (dof-1)*(gj-1)+jdof;
                        if (gj-1<=nnode) gkj=gkj+gj-1;
                        else gkj=gkj+nnode;
                        gestif[(gki-1)*15+gkj-1]=gestif[(gki-1)*15+gkj-1]+estif[(ki-1)*9+kj-1];
                    }
                }
            }
        }
    }
    return;
}
