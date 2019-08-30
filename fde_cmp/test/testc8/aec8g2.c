/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = aec8g2.c
Version:2.2
Time of release:2019-08-30 13:14:16
All rights reserved by ECTEC Corporation, and person or
organization using Original software to generated these code,anyone
else must get written permission from ECTEC Corporation to
copy a part or whole of this code.
The Code GenID is:
22565914_000906E9061008007FFAFBFFBFEBFBFF_005056C00001
Copyright is protected from:2017-2030
**************************************************************/
#include "felac.h"
double nx,ny,nz;
int nnode,ngaus,ndisp,nrefc,ncoor,nvar;
double vol,det,weigh,stif,fact,shear,r0;
int nvard[4],kdord[4],kvord[72];
double refc[24],gaus[9];
/* .... nnode ---- the number of nodes
   .... ngaus ---- the number of numerical integral points
   .... ndisp ---- the number of unknown functions
   .... nrefc ---- the number of reference coordinates
   .... nvar ---- the number of unknown varibles var
   .... refc ---- reference coordinates at integral points
   .... gaus ---- weight number at integral points
   .... nvard ---- the number of var for each unknown
   .... kdord ---- the highest differential order for each unknown
   .... kvord ---- var number at integral points for each unknown */
double coor[4];
double coorr[24];
double rctr[9],crtr[9];
/*   .... rctr ---- jacobi's matrix
     .... crtr ---- inverse matrix of jacobi's matrix */
void dshap(double (*shap)(double *,int),
           double *,double *,int,int,int);
void dcoor(double (*shap)(double *,int),
           double *,double *,double *,int,int,int);
double invm(int,double *,double *);
double inver_rc(int,int,double *,double *);
void dcoef(double (*shap)(double *,int),
           double *,double *, double *,int,int,int);
static void initial();
static void tran_coor(double *,double *,double *,double *);
static double ftran_coor(double *,int);
static void shap_u(double *,double *);
static double fshap_u(double *,int);
static void shap_v(double *,double *);
static double fshap_v(double *,int);
static void shap_w(double *,double *);
static double fshap_w(double *,int);
void shapn(int,int,int,double *,double *,double *,int,int,int);
void shapc(int,int,int,double *,double *,double *,int,int,int);
/* subroutine */
void aec8g2(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)
double coora[24],*coefa,*prmt,estif[576],*emass,*edamp,*eload;
int num,ibegin;
/* .... coora ---- nodal coordinate value
   .... coefa ---- nodal coef value
   .... estif ---- element stiffness
   .... emass ---- element mass matrix
   .... edamp ---- element damping matrix
   .... eload ---- element load vector
   .... num   ---- element no. */
{
    double refcoor[4]= {0.0,0.0,0.0,0.0};
    double eexx[25],eeyy[25],eezz[25],eeyz[25],
           eexz[25],eexy[25];
    double x,y,z,rx,ry,rz;
    double elump[25];
    static double ru[256],rv[256],rw[256],cu[32],cv[32],cw[32];
    /* .... store shape functions and their partial derivatives
         .... for all integral points */
    int i,j,igaus;
    int ig_u,ig_v,ig_w,iv,jv;
    double pe,pv,fx,fy,fz,rou,alpha;
    pe=prmt[1];
    pv=prmt[2];
    fx=prmt[3];
    fy=prmt[4];
    fz=prmt[5];
    rou=prmt[6];
    alpha=prmt[7];
// .... initialize the basic data
    if (num==ibegin) initial();
    for (i=1; i<=3; ++i)
        for (j=1; j<=8; ++j)
            coorr[(i-1)*(8)+j-1]=coora[(i-1)*(8)+j-1];
    for (i=1; i<=24; ++i)
    {
        eload[i]=0.0;
        for (j=1; j<=24; ++j)
        {
            estif[(i-1)*(24)+j-1]=0.0;
        }
    }
    for (igaus=1; igaus<=ngaus; ++igaus)
    {
        for (i=1; i<=nrefc; ++i) refcoor[i]=refc[(i-1)*(8)+igaus-1];
        tran_coor(refcoor,coor,coorr,rctr);
// .... coordinate caculation by reference coordinates
// det = invm(ncoor,rctr,crtr);
        det = inver_rc(nrefc,ncoor,rctr,crtr);
        /* .... coordinate transfer from reference to original system
           .... rctr ---- jacobi's matrix
           .... crtr ---- inverse matrix of jacobi's matrix */
        x=coor[1];
        y=coor[2];
        z=coor[3];
        rx=refcoor[1];
        ry=refcoor[2];
        rz=refcoor[3];
        ig_u=(igaus-1)*8*4;
        ig_v=(igaus-1)*8*4;
        ig_w=(igaus-1)*8*4;
        if (num>ibegin) goto l2;
// .... the following is the shape function caculation
        shap_u(refcoor,&ru[ig_u]);
        shap_v(refcoor,&rv[ig_v]);
        shap_w(refcoor,&rw[ig_w]);
l2:
        /* .... the following is the shape function transformation
          .... from reference coordinates to original coordinates */
        shapn(nrefc,ncoor,8,&ru[ig_u],cu,crtr,1,4,4);
        shapn(nrefc,ncoor,8,&rv[ig_v],cv,crtr,1,4,4);
        shapn(nrefc,ncoor,8,&rw[ig_w],cw,crtr,1,4,4);
        weigh=det*gaus[igaus];
        for (i=1; i<=24; ++i)
        {
            eexx[i] = 0.0;
            eeyy[i] = 0.0;
            eezz[i] = 0.0;
            eeyz[i] = 0.0;
            eexz[i] = 0.0;
            eexy[i] = 0.0;
        }
        vol = 1.0;
        fact = pe/(1.0+pv)/(1.0-pv*2.0)*vol;
        shear = (0.5-pv);
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+2-1] ;
            eexx[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+3-1] ;
            eeyy[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+4-1] ;
            eezz[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+4-1] ;
            eeyz[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+3-1] ;
            eeyz[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+4-1] ;
            eexz[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+2-1] ;
            eexz[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+3-1] ;
            eexy[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+2-1] ;
            eexy[iv]+=stif;
        }
// .... the following is the stiffness computation
        for (iv=1; iv<=24; ++iv)
        {
            for (jv=1; jv<=24; ++jv)
            {
                stif=+eexx[iv]*eexx[jv]*(1.-pv)*fact
                     +eexx[iv]*eeyy[jv]*pv*fact
                     +eexx[iv]*eezz[jv]*pv*fact
                     +eeyy[iv]*eexx[jv]*pv*fact
                     +eeyy[iv]*eeyy[jv]*(1.-pv)*fact
                     +eeyy[iv]*eezz[jv]*pv*fact
                     +eezz[iv]*eexx[jv]*pv*fact
                     +eezz[iv]*eeyy[jv]*pv*fact
                     +eezz[iv]*eezz[jv]*(1.-pv)*fact
                     +eeyz[iv]*eeyz[jv]*shear*fact
                     +eexz[iv]*eexz[jv]*shear*fact
                     +eexy[iv]*eexy[jv]*shear*fact;
                estif[(iv-1)*(24)+jv-1]=estif[(iv-1)*(24)+jv-1]+stif*weigh;
            }
        }
// .... the following is the load vector computation
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+1-1]*fx*vol;
            eload[iv]+=stif*weigh;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+1-1]*fy*vol;
            eload[iv]+=stif*weigh;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+1-1]*fz*vol;
            eload[iv]+=stif*weigh;
        }
    }
l999:
    return;
}

static void initial()
{
// .... initial data
// .... refc ---- reference coordinates at integral points
// .... gaus ---- weight number at integral points
// .... nvard ---- the number of var for each unknown
// .... kdord ---- the highest differential order for each unknown
// .... kvord ---- var number at integral points for each unknown
    ngaus=  8;
    ndisp=  3;
    nrefc=  3;
    ncoor=  3;
    nvar = 24;
    nnode=  8;
    kdord[1]=1;
    nvard[1]=8;
    kvord[(1-1)*(3)+1-1]=1;
    kvord[(2-1)*(3)+1-1]=4;
    kvord[(3-1)*(3)+1-1]=7;
    kvord[(4-1)*(3)+1-1]=10;
    kvord[(5-1)*(3)+1-1]=13;
    kvord[(6-1)*(3)+1-1]=16;
    kvord[(7-1)*(3)+1-1]=19;
    kvord[(8-1)*(3)+1-1]=22;
    kdord[2]=1;
    nvard[2]=8;
    kvord[(1-1)*(3)+2-1]=2;
    kvord[(2-1)*(3)+2-1]=5;
    kvord[(3-1)*(3)+2-1]=8;
    kvord[(4-1)*(3)+2-1]=11;
    kvord[(5-1)*(3)+2-1]=14;
    kvord[(6-1)*(3)+2-1]=17;
    kvord[(7-1)*(3)+2-1]=20;
    kvord[(8-1)*(3)+2-1]=23;
    kdord[3]=1;
    nvard[3]=8;
    kvord[(1-1)*(3)+3-1]=3;
    kvord[(2-1)*(3)+3-1]=6;
    kvord[(3-1)*(3)+3-1]=9;
    kvord[(4-1)*(3)+3-1]=12;
    kvord[(5-1)*(3)+3-1]=15;
    kvord[(6-1)*(3)+3-1]=18;
    kvord[(7-1)*(3)+3-1]=21;
    kvord[(8-1)*(3)+3-1]=24;
    refc[(1-1)*(8)+1-1]=0.577350269189626;
    refc[(2-1)*(8)+1-1]=0.577350269189626;
    refc[(3-1)*(8)+1-1]=0.577350269189626;
    gaus[1]=1.0;
    refc[(1-1)*(8)+2-1]=0.577350269189626;
    refc[(2-1)*(8)+2-1]=0.577350269189626;
    refc[(3-1)*(8)+2-1]=-0.577350269189626;
    gaus[2]=1.0;
    refc[(1-1)*(8)+3-1]=0.577350269189626;
    refc[(2-1)*(8)+3-1]=-0.577350269189626;
    refc[(3-1)*(8)+3-1]=0.577350269189626;
    gaus[3]=1.0;
    refc[(1-1)*(8)+4-1]=0.577350269189626;
    refc[(2-1)*(8)+4-1]=-0.577350269189626;
    refc[(3-1)*(8)+4-1]=-0.577350269189626;
    gaus[4]=1.0;
    refc[(1-1)*(8)+5-1]=-0.577350269189626;
    refc[(2-1)*(8)+5-1]=0.577350269189626;
    refc[(3-1)*(8)+5-1]=0.577350269189626;
    gaus[5]=1.0;
    refc[(1-1)*(8)+6-1]=-0.577350269189626;
    refc[(2-1)*(8)+6-1]=0.577350269189626;
    refc[(3-1)*(8)+6-1]=-0.577350269189626;
    gaus[6]=1.0;
    refc[(1-1)*(8)+7-1]=-0.577350269189626;
    refc[(2-1)*(8)+7-1]=-0.577350269189626;
    refc[(3-1)*(8)+7-1]=0.577350269189626;
    gaus[7]=1.0;
    refc[(1-1)*(8)+8-1]=-0.577350269189626;
    refc[(2-1)*(8)+8-1]=-0.577350269189626;
    refc[(3-1)*(8)+8-1]=-0.577350269189626;
    gaus[8]=1.0;
    return;
}


// void dshap(double (*shap)(double *,double *,int),double *,^shpr[][8],int,int,int);
static void shap_u(refc,shpr)
double *refc,shpr[32];
/* compute shape functions and their partial derivatives
 shapr ---- store shape functions and their partial derivatives */
{
    double (*shap)(double *,int)=&fshap_u;
// extern void dshap(shap,double *,double *,int,int,int);
    dshap(shap,refc,shpr,3,8,1);
    /* shape function and their derivatives computation
     compute partial derivatives by centered difference
     which is in the file cshap.c of felac library */
    return;
}

static double fshap_u(double *refc,int n)
// shape function caculation
{
// extern double *coor;
    double rx,ry,rz;
    double x,y,z,fval;
    x=coor[1];
    y=coor[2];
    z=coor[3];
    rx=refc[1];
    ry=refc[2];
    rz=refc[3];
    switch (n)
    {
    case 1:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 2:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 3:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 4:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 5:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 6:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 7:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
    case 8:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
//   default:
    }
    return fval;
}
static void shap_v(refc,shpr)
double *refc,shpr[32];
/* compute shape functions and their partial derivatives
 shapr ---- store shape functions and their partial derivatives */
{
    double (*shap)(double *,int)=&fshap_v;
// extern void dshap(shap,double *,double *,int,int,int);
    dshap(shap,refc,shpr,3,8,1);
    /* shape function and their derivatives computation
     compute partial derivatives by centered difference
     which is in the file cshap.c of felac library */
    return;
}

static double fshap_v(double *refc,int n)
// shape function caculation
{
// extern double *coor;
    double rx,ry,rz;
    double x,y,z,fval;
    x=coor[1];
    y=coor[2];
    z=coor[3];
    rx=refc[1];
    ry=refc[2];
    rz=refc[3];
    switch (n)
    {
    case 1:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 2:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 3:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 4:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 5:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 6:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 7:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
    case 8:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
//   default:
    }
    return fval;
}
static void shap_w(refc,shpr)
double *refc,shpr[32];
/* compute shape functions and their partial derivatives
 shapr ---- store shape functions and their partial derivatives */
{
    double (*shap)(double *,int)=&fshap_w;
// extern void dshap(shap,double *,double *,int,int,int);
    dshap(shap,refc,shpr,3,8,1);
    /* shape function and their derivatives computation
     compute partial derivatives by centered difference
     which is in the file cshap.c of felac library */
    return;
}

static double fshap_w(double *refc,int n)
// shape function caculation
{
// extern double *coor;
    double rx,ry,rz;
    double x,y,z,fval;
    x=coor[1];
    y=coor[2];
    z=coor[3];
    rx=refc[1];
    ry=refc[2];
    rz=refc[3];
    switch (n)
    {
    case 1:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 2:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.;
        break;
    case 3:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 4:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.;
        break;
    case 5:
        fval=+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 6:
        fval=+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.;
        break;
    case 7:
        fval=+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
    case 8:
        fval=+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.;
        break;
//   default:
    }
    return fval;
}
static void tran_coor(double *refc,double *coor,double *coorr,double *rc)
/* compute coordinate value and jacobi's matrix rc
 by reference coordinate value */
{
    double (*shap)(double *,int)=&ftran_coor;
// extern void dcoor(shap,double *,double *,double *,
//  int,int,int);
    dcoor(shap,refc,coor,rc,3,3,1);
    /* coordinate value and their partial derivatives caculation
     compute partial derivatives by centered difference
     which is in the file cshap.c of felac library */
    return;
}

static double ftran_coor(double *refc,int n)
/* coordinate transfer function caculation */
{
    double rx,ry,rz,fval;
    double x[9],y[9],z[9];
    int j;
    for (j=1; j<=8; ++j)
    {
        x[j]=coorr[(1-1)*(8)+j-1];
        y[j]=coorr[(2-1)*(8)+j-1];
        z[j]=coorr[(3-1)*(8)+j-1];
    }
    rx=refc[1];
    ry=refc[2];
    rz=refc[3];
    switch (n)
    {
    case 1:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*x[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*x[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*x[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*x[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*x[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*x[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*x[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*x[8];
        break;
    case 2:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*y[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*y[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*y[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*y[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*y[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*y[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*y[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*y[8];
        break;
    case 3:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*z[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*z[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*z[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*z[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*z[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*z[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*z[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*z[8];
        break;
        //default:
    }
    return fval;
}

