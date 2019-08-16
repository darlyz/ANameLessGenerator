extern void nsxyzw(double *,double *,double *,double *,double *,double *,double *,int);
void nsw10(gcoorr,gcoefr,prmt,gestif,gemass,gedamp,geload,num)
double gcoorr[30],gcoefr[30],*prmt,gestif[1156];
double *gemass,*gedamp,*geload;
int num;
{
    double coorr[12],coefr[12],estif[256];
    double emass[100],edamp[100],eload[100];
    int n,i,j,ki,kj,gi,gj,gki,gkj,nnode,gnnode,dim,dof,idof,jdof;
    int nelem,node[32];
    nnode = 4;
    gnnode = 10;
    dof = 4;
    dim = 3;
    nelem = 8;
    node[(1-1)*4+1-1]=1;
    node[(1-1)*4+2-1]=5;
    node[(1-1)*4+3-1]=7;
    node[(1-1)*4+4-1]=8;
    node[(2-1)*4+1-1]=8;
    node[(2-1)*4+2-1]=5;
    node[(2-1)*4+3-1]=7;
    node[(2-1)*4+4-1]=9;
    node[(3-1)*4+1-1]=5;
    node[(3-1)*4+2-1]=2;
    node[(3-1)*4+3-1]=6;
    node[(3-1)*4+4-1]=9;
    node[(4-1)*4+1-1]=5;
    node[(4-1)*4+2-1]=6;
    node[(4-1)*4+3-1]=7;
    node[(4-1)*4+4-1]=9;
    node[(5-1)*4+1-1]=7;
    node[(5-1)*4+2-1]=6;
    node[(5-1)*4+3-1]=3;
    node[(5-1)*4+4-1]=10;
    node[(6-1)*4+1-1]=7;
    node[(6-1)*4+2-1]=6;
    node[(6-1)*4+3-1]=10;
    node[(6-1)*4+4-1]=9;
    node[(7-1)*4+1-1]=8;
    node[(7-1)*4+2-1]=10;
    node[(7-1)*4+3-1]=4;
    node[(7-1)*4+4-1]=9;
    node[(8-1)*4+1-1]=8;
    node[(8-1)*4+2-1]=7;
    node[(8-1)*4+3-1]=10;
    node[(8-1)*4+4-1]=9;
    for (i=1; i<=34; ++i)
    {
        gemass[i]=0.0;
        gedamp[i]=0.0;
        geload[i]=0.0;
        for (j=1; j<=34; ++j)
        {
            gestif[(i-1)*34+j-1]=0.0;
        }
    }

    for (n=1; n<=nelem; ++n)
    {
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*4+i-1];
            for (idof=1; idof<=dim; ++idof)
            {
                coorr[(idof-1)*4+i-1]=gcoorr[(idof-1)*10+gi-1];
                coefr[(idof-1)*4+i-1]=gcoefr[(idof-1)*10+gi-1];
            }
        }
        nsxyzw(coorr,coefr,prmt,estif,emass,edamp,eload,num);
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
                        gestif[(gki-1)*34+gkj-1]=gestif[(gki-1)*34+gkj-1]+estif[(ki-1)*16+kj-1];
                    }
                }
            }
        }
    }
    return;
}
