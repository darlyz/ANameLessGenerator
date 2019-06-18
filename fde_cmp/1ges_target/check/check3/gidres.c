/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = gidres.c
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
#include "felac.h"
int gidmsh(struct coordinates,struct element);
int gidres(coor0)
struct coordinates coor0;
{
    FILE *fp;
    int i,j,dim,knode,ik;
// double *coor,d;
    int *mlgnode;
    char str[100];
    knode = coor0.knode;
    dim = coor0.dim;
    if (it==0) it=1;
    if ((it%nstep)!=0) goto l100;
    ik = it/nstep;
    if ((fp = fopen("./check3.gid/check3.post.res","a"))==NULL)
    {
        printf("cat:cannot open %s\n", "check3.post.res");
        return  1;
    }
    fprintf(fp,"%s%d%s\n","Result \"unoda0\" \"Load Analysis\"  ",ik," Vector OnNodes");
    fprintf(fp,"%s\n","ComponentNames \"u\" \"v\" \"w\" ");
    fprintf(fp,"%s\n","Values");
    for (j=1; j<=knode; ++j)
    {
        fprintf(fp,"%d",j );
        fprintf(fp," %e",unoda[0*knode+j-1]);
        fprintf(fp," %e",unoda[1*knode+j-1]);
        fprintf(fp," %e",unoda[2*knode+j-1]);
        fprintf(fp,"\n");
    }
    fprintf(fp,"%s\n","End Values");
    fclose(fp);
l100:
    return 0;
}
