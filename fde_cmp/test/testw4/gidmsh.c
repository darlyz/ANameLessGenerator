/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = gidmsh.c
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
#include "felac.h"
int gidmsh(coor0,elem)
struct coordinates coor0;
struct element elem;
{
    FILE *fp;
    int i,j,n,dim,knode,*nnode,*node,*nelem;
    double *coor,d;
    int *mlgnode;
    char str[100];
    knode = coor0.knode;
    dim = coor0.dim;
    coor = coor0.coor;
    nnode = elem.nnode;
    node = elem.node;
    nelem = elem.nelem;
    n = 0;
    if ((fp = fopen("./testw4.gid/testw4.post.msh","w"))==NULL)
    {
        printf("cat:cannot open %s\n", "testw4.post.msh");
        return  1;
    }
    fprintf(fp,"%s\n","Mesh \"aew4g2\" Dimension 3 Elemtype Tetrahedra Nnode 4");
    fprintf(fp,"%s\n","Coordinates");
    for (j=1; j<=knode; ++j)
    {
        fprintf(fp,"%d",j);
        for (i=1; i<=dim; ++i)
        {
            fprintf(fp," %e",coor[(i-1)*knode+j-1]);
        }
        fprintf(fp,"\n");
    }
    fprintf(fp,"%s\n","End coordinates");
    fprintf(fp,"%s\n","Elements");
    for (i=1; i<=nelem[1]; ++i)
    {
        fprintf(fp,"%d",i);
        for (j=1; j<nnode[1]; ++j)
        {
            fprintf(fp," %d",node[++n]);
        }
        n=n+1;
        if(node[n]>0)
        {
            fprintf(fp," %d\n",node[n]);
        }
        else
        {
            fprintf(fp," %d\n",100-node[n]);
        }
    }
    fprintf(fp,"%s\n","End elements");
    fclose(fp);
    if ((fp = fopen("./testw4.gid/testw4.post.res","w"))==NULL)
    {
        ;
        printf("cat:cannot open %s\n", "testw4.post.res");
        return  1;
    }
    fprintf(fp,"%s\n","GID Post Results File 1.0");
    fclose(fp);
    return 0;
}
