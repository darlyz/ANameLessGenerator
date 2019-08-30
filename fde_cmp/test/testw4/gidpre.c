/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = gidpre.c
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
#include <string.h>
#define MAXSTRLEN 500

int getid(FILE *fp,int,int,int *);
int getrd(FILE *fp,int,int,double *);
int getelem(FILE *fp,int,int,struct element *);
int getmate(FILE *fp,struct element *);
void goto_next_valid_line( FILE *fp);
void skip_lines( FILE *fp, int lines);
void show(FILE *fp, int lines);

int gidpre(void)
{
    FILE *fp;
    int argc,knode;
    char *argv[2];
    int m,k,n,mkd,em = 0,ntype;
    double *coor,d;
    char mystring [160];
    if ((fp = fopen("time0","r"))==NULL)
    {
        printf("cat:cannot open %s\n", "time0");
        /*system("pause");*/ exit(1);
    }
    fgets(mystring,4,fp);
    if(strcmp(mystring,"\xEF\xBB\xBF")!=0)rewind(fp);
    fscanf(fp,"%lf",&tmax);
    fgets(mystring,160,fp);
    fscanf(fp,"%lf",&dt);
    fgets(mystring,160,fp);
    fscanf(fp,"%d",&nstep);
    fgets(mystring,160,fp);
    fscanf(fp,"%d",&itnmax);
    fgets(mystring,160,fp);
    fscanf(fp,"%lf",&tolerance);
    fgets(mystring,160,fp);
    fscanf(fp,"%lf",&dampalfa);
    fgets(mystring,160,fp);
    fscanf(fp,"%lf",&dampbeta);
    fgets(mystring,160,fp);
    fclose(fp);
    itn=1;
    end=0;
    it=0;
    stop=0;
    time_now=0.0;
    setsolver(default_solver,default_solvpara);
    /*
     if ((fp = fopen(argv[1],"r"))==NULL) {
     printf("cat:cannot open %s\n", *argv);
     return 1; }
     fscanf(fp,"%d",&n);
     fgets(mystring,160,fp);
     coor0.knode = n;
     knode = coor0.knode;
    // coor = coor0.coor;
    // getrd(fp,dim,knode,coor);
    */
    if ((fp = fopen("./testw4.gid/testw4.dat","r"))==NULL)
    {
        printf("cat:cannot open %s\n","./testw4.gid/testw4.dat");
        /*system("pause");*/ exit(1);
    }
    goto_next_valid_line(fp);
    fscanf(fp,"%d",&n);
    fgets(mystring,160,fp);
    coor0.knode = n;
    knode = n;
    dim = 3;
    coor0.dim = dim;
    k = knode*dim;
    coor0.coor = (double *) calloc(k,sizeof(double));
    coor = coor0.coor;
    getrd(fp,dim,knode,coor);
    nbdetype = 1;
    dofa = 3;
    inita = 0;
    mkd = knode*dofa;
    ubfa = (double *) calloc(mkd,sizeof(double));
    ida = (int *) calloc(mkd,sizeof(int));
    unoda = (double *) calloc(mkd*3,sizeof(double));
    for (m=0; m<(mkd*3); m++) unoda[m] = 0.0;
    m = getid(fp,dofa,knode,ida);
    m = getrd(fp,dofa,knode,ubfa);
    ntype = 1;
    m = getelem(fp,ntype,em,&elema);
    fclose(fp);
    if ((fp = fopen("testw4.mat","r"))==NULL)
    {
        printf("cat:cannot open %s\n","testw4.mat");
        /*system("pause");*/ exit(1);
    }
    m = getmate(fp,&elema);
    fclose(fp);

    return 0;
}

int getrd( fp, dimdof, knode, data)
FILE *fp;
int dimdof, knode;
double *data;
{
    int i, j, k, row, col;
    double d;
    for (j=0; j< dimdof* knode; j++) data[j] = 0.0;
    goto_next_valid_line(fp);
    fscanf(fp, "%d", &row);
    fscanf(fp, "%d", &col);
    for (i = 0; i< row; ++i)
    {
        fscanf( fp, "%d", &k);
        for( j= 0; j< col; ++j)
        {
            fscanf( fp, "%lf", &(data[knode*j + k - 1]));
        }
    }
    return k;
}

/*
int getid(fp,n,m,ip)
FILE *fp;
int n,m;
int *ip;
{
    int i,j,k;
    int d;
    char mystring [160];
    for (j=0; j<m*n; j++) ip[j] = 1;
    k = 1;
    fgets(mystring,160,fp);
    while (k>0)
    {
        fscanf(fp,"%d",&k);
        if (k>0)
        {
            for (i=0; i<n; i++)
            {
                fscanf(fp,"%d",&d);
                ip[m*i+k-1] = d;
            }
        }
    }
    return k;
}
*/

int getid( fp, dimdof, knode, data)
FILE *fp;
int dimdof, knode;
int *data;
{
    int i, j, k, row, col;
    double d;
    k=0;
    for (j=0; j< dimdof* knode; j++) data[j] = 1;
    goto_next_valid_line(fp);
    fscanf(fp, "%d", &row);
    fscanf(fp, "%d", &col);
    for (i = 0; i< row; ++i)
    {
        fscanf( fp, "%d", &k);
        for( j= 0; j< col; ++j)
        {
            fscanf( fp, "%d", &(data[knode*j + k - 1]));
        }
    }
    return k;
}

/*
int getelem(FILE *fp,int ntype,int em,struct element *elem)
{
    int i,j,k,m,n;
    int d,*node;
    int l;
    char mystring [160];
    node = (int *) calloc(maxnode,sizeof(int));
    (*elem).ntype = ntype;
    m=em;
    (*elem).nnode[1]=m;
//  fgets(mystring,160,fp);
    n=0;
    l=0;
    j=1;
    while (j<=ntype)
    {
        fgets(mystring,160,fp);
        fscanf(fp,"%d",&k);
        if (k<0)
        {
            m = 1-k;
            j++;
            (*elem).nnode[j]=m;
            l=0;
        }
        else
        {
            for (i=0; i<m; i++)
            {
                fscanf(fp,"%d",&d);
                n++;
                node[n-1] = d;
            }
            l++;
            (*elem).nelem[j]=l;
        }
    }
    (*elem).node = (int *) calloc(n+1,sizeof(int));
    for (j=0; j<n; ++j)
    {
        (*elem).node[j+1] = node[j];
    }
    free(node);
    return k;
}
*/


int getelem(FILE *fp,int ntype,int em,struct element *elem)
{
    int i, j, k, n, temp;
    int nodesum;    /* may be long long int */
    int *node;

    fpos_t pos;

    fgetpos(fp, &pos);

    nodesum = 0;
    (*elem).ntype = ntype;

    /* count the number of nodes (including material #) of elements in current field */
    for (i = 1; i<= ntype; ++i)
    {
        goto_next_valid_line(fp);

        fscanf(fp, "%d", &((*elem).nelem[i]) );
        fscanf(fp, "%d", &((*elem).nnode[i]) );
        nodesum += (*elem).nelem[i] * (*elem).nnode[i];
        skip_lines(fp, (*elem).nelem[i]+1 );
    }

    (*elem).node = (int *) calloc(nodesum+1,sizeof(int));
    node = (*elem).node;

    /* start to read node[] */
    fsetpos( fp, &pos);
    n =0;

    for ( i = 1; i<= ntype; ++i)
    {

        goto_next_valid_line(fp);
        skip_lines(fp,1);

        for (j =0 ; j< (*elem).nelem[i]; ++j)
        {
            fscanf(fp, "%d", &temp);
            for ( k= 0; k < (*elem).nnode[i]; ++k)
            {
                fscanf(fp, "%d", &(node[++n]));    // node[] index start from 1
            }
        }
    }

    return 0;
}


int getmate(FILE *fp,struct element *elem)
{
    int n,i,j,m,k;
    double r,*mate;
    char mystring [160];
    mate = (double *) calloc(maxmate,sizeof(double));
    m = 0;
    fscanf(fp,"%d",&k);
    (*elem).ntype = k;
    fgets(mystring,160,fp);
    for (n=1; n<=(*elem).ntype; n++)
    {
        fscanf(fp,"%d",&k);
        (*elem).nmate[n] = k;
        fscanf(fp,"%d",&k);
        (*elem).nprmt[n] = k;
        for (i=1; i<=(*elem).nmate[n]; i++)
        {
            for (j=1; j<=(*elem).nprmt[n]; j++)
            {
                fscanf(fp,"%lf",&r);
                mate[++m] = r;
            }
//           do c=getc(fp); while (c|='\n');
            fgets(mystring,160,fp);
        }
    }
    (*elem).mate = (double *) calloc(m+1,sizeof(double));
    for (i=1; i<=m; ++i) (*elem).mate[i] = mate[i];
    free(mate);
    return m;
}

void chid(coor0,dof,nodvar,elem)
struct coordinates coor0;
int dof,*nodvar;
struct element elem;
{
    int numel,nn,ityp,nelem,nnode,nne,n0;
    int i,j,node[500],inod,nodi,kvar;
    int dim,knode;
    double *coor;
    dim = coor0.dim;
    knode = coor0.knode;
    coor = coor0.coor;
    kvar = knode*dof;
    numel=0;
    nn=0;
    for (ityp=1; ityp<=elem.ntype; ++ityp)
    {
        /*2000*/
        nelem=elem.nelem[ityp];
        nnode=elem.nnode[ityp];
        nne = nnode-1;
        n0=nne;
        if (nne==6) n0=3;
        if (nne==9) n0=4;
        if (nne==10) n0=4;
        if (nne==27) n0=8;
        if (n0!=nne)
        {
            for (i=1; i<=nelem; ++i)
            {
                for (j=1; j<=nnode; ++j) node[j]=elem.node[++nn];
                for (inod=n0+1; inod<=nne; ++inod)
                {
                    nodi=node[inod];
                    nodvar[(dof-1)*knode+nodi-1]=0;
                }
            }
        }
    } /*2000*/
}

/*
去掉字符串首尾的 \x20 \r \n 字符
*/
void trimString(char *str)
{
    char *start = str - 1;
    char *end = str;
    char *p = str;
    while(*p)
    {
        switch(*p)
        {
        case ' ':
        case '\r':
        case '\n':
        {
            if(start + 1==p)
                start = p;
        }
        break;
        default:
            break;
        }
        ++p;
    }
    //现在来到了字符串的尾部 反向向前
    --p;
    ++start;
    if(*start == 0)
    {
        *str = 0 ;
        return;
    }
    end = p + 1;
    while(p > start)
    {
        switch(*p)
        {
        case ' ':
        case '\r':
        case '\n':
        {
            if(end - 1 == p)
                end = p;
        }
        break;
        default:
            break;
        }
        --p;
    }
    memmove(str,start,end-start);
    // printf("start: %d\n", (long long int)start );
    // printf("end: %d\n", (long long int)(end));
    *( str + (long long int)end - (long long int)(start) ) = 0;
    // system("pause");
}

int isNumber(char ch)
{
    if ( ch >= '0' && ch <= '9') return 1;
    else return 0;
}


void goto_next_valid_line( FILE *fp)
{
    char tempstr[MAXSTRLEN];
    fpos_t pos;

    fgetpos(fp, &pos);
    fgets(tempstr,MAXSTRLEN,fp);
    trimString(tempstr);
    while (! isNumber(tempstr[0]) )
    {
        fgetpos( fp, &pos);
        fgets(tempstr,MAXSTRLEN,fp);
        trimString( tempstr );
    }
    // print("in gotoNextValidLine, %c, tempstr=%s, pos: %ld\n", tempstr[0], tempstr, pos);
    fsetpos( fp, &pos);

    return;
}


void skip_lines( FILE *fp, int lines)
{
    int i;
    char tempstr[MAXSTRLEN];
    for ( i = 0; i< lines; ++i)
    {
        fgets( tempstr, MAXSTRLEN, fp);
    }
    return;
}

void show(FILE *fp, int lines)
{
    int i;
    char tempstr[MAXSTRLEN];
    printf("showing %d lines of file:\n", lines);
    for ( i = 0; i< lines; ++i)
    {
        fgets( tempstr, MAXSTRLEN, fp);
        printf("%s", tempstr);
    }
}

