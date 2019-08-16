extern void nsxyq(double *,double *,double *,double *,double *,double *,double *,int);
void nsq9(gcoorr,gcoefr,prmt,gestif,gemass,gedamp,geload,num)
double gcoorr[18],gcoefr[18],*prmt,gestif[484];
double *gemass,*gedamp,*geload;
int num;
{
    double coorr[8],coefr[8],estif[144];
    double emass[100],edamp[100],eload[100];
    int n,i,j,ki,kj,gi,gj,gki,gkj,nnode,gnnode,dim,dof,idof,jdof;
    int nelem,node[16];
    nnode = 4;
    gnnode = 9;
    dof = 3;
    dim = 2;
    nelem = 4;
    node[(1-1)*4+1-1]=1;
    node[(1-1)*4+2-1]=5;
    node[(1-1)*4+3-1]=9;
    node[(1-1)*4+4-1]=8;
    node[(2-1)*4+1-1]=5;
    node[(2-1)*4+2-1]=2;
    node[(2-1)*4+3-1]=6;
    node[(2-1)*4+4-1]=9;
    node[(3-1)*4+1-1]=9;
    node[(3-1)*4+2-1]=6;
    node[(3-1)*4+3-1]=3;
    node[(3-1)*4+4-1]=7;
    node[(4-1)*4+1-1]=8;
    node[(4-1)*4+2-1]=9;
    node[(4-1)*4+3-1]=7;
    node[(4-1)*4+4-1]=4;
    for (i=1; i<=22; ++i)
    {
        gemass[i]=0.0;
        gedamp[i]=0.0;
        geload[i]=0.0;
        for (j=1; j<=22; ++j)
        {
            gestif[(i-1)*22+j-1]=0.0;
        }
    }
    for (n=1; n<=nelem; ++n)
    {
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*4+i-1];
            for (idof=1; idof<=dim; ++idof)
            {
                coorr[(idof-1)*4+i-1]=gcoorr[(idof-1)*9+gi-1];
                coefr[(idof-1)*4+i-1]=gcoefr[(idof-1)*9+gi-1];
            }
        }
        nsxyq(coorr,coefr,prmt,estif,emass,edamp,eload,num);
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*4+i-1];
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
                    gj = node[(n-1)*4+j-1];
                    for (jdof=1; jdof<=dof-1; ++jdof)
                    {
                        kj = (j-1)*dof+jdof;
                        gkj = (dof-1)*(gj-1)+jdof;
                        if (gj-1<=nnode) gkj=gkj+gj-1;
                        else gkj=gkj+nnode;
                        gestif[(gki-1)*22+gkj-1]=gestif[(gki-1)*22+gkj-1]+estif[(ki-1)*12+kj-1];
                    }
                }
            }
        }
    }
    return;
}
