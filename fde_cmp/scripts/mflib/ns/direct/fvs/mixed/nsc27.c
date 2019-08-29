extern void nsxyzc(double *,double *,double *,double *,double *,double *,double *,int);
void nsc27(gcoorr,gcoefr,prmt,gestif,gemass,gedamp,geload,num)
double gcoorr[81],gcoefr[81],*prmt,gestif[7921];
double *gemass,*gedamp,*geload;
int num;
{
    double coorr[24],coefr[24],estif[1024];
    double emass[100],edamp[100],eload[100];
    int n,i,j,ki,kj,gi,gj,gki,gkj,nnode,gnnode,dim,dof,idof,jdof;
    int nelem,node[64];
    nnode = 8;
    gnnode = 27;
    dof = 4;
    dim = 3;
    nelem = 8;
    node[(1-1)*8+1-1]=1;
    node[(1-1)*8+2-1]=9;
    node[(1-1)*8+3-1]=21;
    node[(1-1)*8+4-1]=12;
    node[(1-1)*8+5-1]=13;
    node[(1-1)*8+6-1]=22;
    node[(1-1)*8+7-1]=27;
    node[(1-1)*8+8-1]=25;
    node[(2-1)*8+1-1]=9;
    node[(2-1)*8+2-1]=2;
    node[(2-1)*8+3-1]=10;
    node[(2-1)*8+4-1]=21;
    node[(2-1)*8+5-1]=22;
    node[(2-1)*8+6-1]=14;
    node[(2-1)*8+7-1]=23;
    node[(2-1)*8+8-1]=27;
    node[(3-1)*8+1-1]=12;
    node[(3-1)*8+2-1]=21;
    node[(3-1)*8+3-1]=11;
    node[(3-1)*8+4-1]=4;
    node[(3-1)*8+5-1]=25;
    node[(3-1)*8+6-1]=27;
    node[(3-1)*8+7-1]=24;
    node[(3-1)*8+8-1]=16;
    node[(4-1)*8+1-1]=21;
    node[(4-1)*8+2-1]=10;
    node[(4-1)*8+3-1]=3;
    node[(4-1)*8+4-1]=11;
    node[(4-1)*8+5-1]=27;
    node[(4-1)*8+6-1]=23;
    node[(4-1)*8+7-1]=15;
    node[(4-1)*8+8-1]=24;
    node[(5-1)*8+1-1]=13;
    node[(5-1)*8+2-1]=22;
    node[(5-1)*8+3-1]=27;
    node[(5-1)*8+4-1]=25;
    node[(5-1)*8+5-1]=5;
    node[(5-1)*8+6-1]=17;
    node[(5-1)*8+7-1]=26;
    node[(5-1)*8+8-1]=20;
    node[(6-1)*8+1-1]=22;
    node[(6-1)*8+2-1]=14;
    node[(6-1)*8+3-1]=23;
    node[(6-1)*8+4-1]=27;
    node[(6-1)*8+5-1]=17;
    node[(6-1)*8+6-1]=6;
    node[(6-1)*8+7-1]=18;
    node[(6-1)*8+8-1]=26;
    node[(7-1)*8+1-1]=25;
    node[(7-1)*8+2-1]=27;
    node[(7-1)*8+3-1]=24;
    node[(7-1)*8+4-1]=16;
    node[(7-1)*8+5-1]=20;
    node[(7-1)*8+6-1]=26;
    node[(7-1)*8+7-1]=19;
    node[(7-1)*8+8-1]=8;
    node[(8-1)*8+1-1]=27;
    node[(8-1)*8+2-1]=23;
    node[(8-1)*8+3-1]=15;
    node[(8-1)*8+4-1]=24;
    node[(8-1)*8+5-1]=26;
    node[(8-1)*8+6-1]=18;
    node[(8-1)*8+7-1]=7;
    node[(8-1)*8+8-1]=19;
    for (i=1; i<=89; ++i)
    {
        gemass[i]=0.0;
        gedamp[i]=0.0;
        geload[i]=0.0;
        for (j=1; j<=89; ++j)
        {
            gestif[(i-1)*89+j-1]=0.0;
        }
    }
    for (n=1; n<=nelem; ++n)
    {
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*8+i-1];
            for (idof=1; idof<=dim; ++idof)
            {
                coorr[(idof-1)*8+i-1]=gcoorr[(idof-1)*27+gi-1];
                coefr[(idof-1)*8+i-1]=gcoefr[(idof-1)*27+gi-1];
            }
        }
        nsxyzc(coorr,coefr,prmt,estif,emass,edamp,eload,num);
        for (i=1; i<=nnode; ++i)
        {
            gi = node[(n-1)*8+i-1];
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
                    gj = node[(n-1)*8+j-1];
                    for (jdof=1; jdof<=dof-1; ++jdof)
                    {
                        kj = (j-1)*dof+jdof;
                        gkj = (dof-1)*(gj-1)+jdof;
                        if (gj-1<=nnode) gkj=gkj+gj-1;
                        else gkj=gkj+nnode;
                        gestif[(gki-1)*89+gkj-1]=gestif[(gki-1)*89+gkj-1]+estif[(ki-1)*32+kj-1];
                    }
                }
            }
        }
    }
    return;
}
