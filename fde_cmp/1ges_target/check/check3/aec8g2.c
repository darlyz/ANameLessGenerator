#include "felac.h"
double nx,ny,nz;
int nnode,ngaus,ndisp,nrefc,ncoor,nvar;
double vol,det,weigh,stif,fact,shear,r0;
double *inelmc8;;
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
double coefr[24];
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
static void coef_shap(double *,double *,double *,double *);
static double fcoef_shap(double *,int);
void shapn(int,int,int,double *,double *,double *,int,int,int);
void shapc(int,int,int,double *,double *,double *,int,int,int);
/* subroutine */
void aec8g2(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)
double coora[24],coefa[24],*prmt,estif[576],*emass,*edamp,*eload;
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
    double coef[4];
    double un,vn,wn;
    double coefd[27],coefc[27];
    double eexx[25],eeyy[25],eezz[25],eeyz[25],
           eexz[25],eexy[25],eplast[25],eplastg[25];
    double x,y,z,rx,ry,rz;
    double elump[25];
    static double ru[256],rv[256],rw[256],cu[32],cv[32],cw[32];
    /* .... store shape functions and their partial derivatives
         .... for all integral points */
    int i,j,igaus;
    int ig_u,ig_v,ig_w,iv,jv;
    double pe,pv,fx,fy,fz,rou,alpha,t0,time1,a,b,prag,dln,shearqrev,factqrev;
    double vi,qnn,shearwave;
    int kq,ntime,ialpha;
    extern double getyield(double *,double *,double *,double,double *,
                           int,double (*f)(),int);
    extern double prager(double *,double *);
    double dev[4],dep[4],e[9],d[9],qrev[9],dwave[9],dsv1[9];
    double ddf[8],ddg[8],ds[8],str[8],p[5];
    static int init=0;
    int m;
// .... initialize the basic data
    if (num==ibegin) initial();
    for (i=1; i<=3; ++i)
        for (j=1; j<=8; ++j)
            coorr[(i-1)*(8)+j-1]=coora[(i-1)*(8)+j-1];
    for (i=1; i<=3; ++i)
        for (j=1; j<=8; ++j)
            coefr[(i-1)*(8)+j-1]=coefa[(i-1)*(8)+j-1];
    for (i=1; i<=24; ++i)
    {
        eload[i]=0.0;
        for (j=1; j<=24; ++j)
        {
            estif[(i-1)*(24)+j-1]=0.0;
        }
    }
    m = ngaus*7;
    if (init==0)
    {
        inelmc8 = (double *) calloc(nelem*m+1,sizeof(double));
        for (i=1; i<=nelem*m; ++i) inelmc8[i]=0.0;
        init = 1;
    }
    pe=prmt[1];
    pv=prmt[2];
    vi=prmt[3];
    fx=prmt[4];
    fy=prmt[5];
    fz=prmt[6];
    p[1]=prmt[7];
    p[2]=prmt[8];
    p[4]=prmt[9];
    qnn=prmt[10];
    rou=prmt[11];
    alpha=prmt[12];
    t0 = 0.0;
    ntime=(tmax-t0)/dt;
    time1=time_now/ntime;
    kq=qnn+0.5;
    p[3]=pv;
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
        coef_shap(refcoor,coef,coefr,coefd);
// .... compute coef functions and their partial derivatives
        un=coef[1];
        vn=coef[2];
        wn=coef[3];
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
        /* .... the coef function transformation
          .... from reference coordinates to original coordinates */
        shapc(nrefc,ncoor,3,coefd,coefc,crtr,2,9,9);
        weigh=det*gaus[igaus];
        for (i=1; i<=24; ++i)
        {
            eexx[i] = 0.0;
            eeyy[i] = 0.0;
            eezz[i] = 0.0;
            eeyz[i] = 0.0;
            eexz[i] = 0.0;
            eexy[i] = 0.0;
            eplast[i] = 0.0;
            eplastg[i] = 0.0;
        }
        vol = 1.0;
        fact=pe/(1.0+pv)/(1.0-2.0*pv);
        shear=(0.5-pv)*fact;
        d[(1-1)*(3)+1-1]=+(1.-pv)*fact;
        d[(1-1)*(3)+2-1]=+pv*fact;
        d[(1-1)*(3)+3-1]=+pv*fact;
        d[(2-1)*(3)+1-1]=+pv*fact;
        d[(2-1)*(3)+2-1]=+(1.-pv)*fact;
        d[(2-1)*(3)+3-1]=+pv*fact;
        d[(3-1)*(3)+1-1]=+pv*fact;
        d[(3-1)*(3)+2-1]=+pv*fact;
        d[(3-1)*(3)+3-1]=+(1.-pv)*fact;
        factqrev=1/vi;
        shearqrev=factqrev;
        qrev[(1-1)*(3)+1-1]=1./3.0*factqrev;
        qrev[(1-1)*(3)+2-1]=-1./6.0*factqrev;
        qrev[(1-1)*(3)+3-1]=-1./6.0*factqrev;
        qrev[(2-1)*(3)+1-1]=-1./6.0*factqrev;
        qrev[(2-1)*(3)+2-1]=1./3.0*factqrev;
        qrev[(2-1)*(3)+3-1]=-1./6.0*factqrev;
        qrev[(3-1)*(3)+1-1]=-1./6.0*factqrev;
        qrev[(3-1)*(3)+2-1]=-1./6.0*factqrev;
        qrev[(3-1)*(3)+3-1]=1./3.0*factqrev;
        det=invm(3,d,e);
        d[(1-1)*(3)+1-1]=e[(1-1)*(3)+1-1];
        d[(1-1)*(3)+2-1]=e[(1-1)*(3)+2-1];
        d[(1-1)*(3)+3-1]=e[(1-1)*(3)+3-1];
        d[(2-1)*(3)+1-1]=e[(2-1)*(3)+1-1];
        d[(2-1)*(3)+2-1]=e[(2-1)*(3)+2-1];
        d[(2-1)*(3)+3-1]=e[(2-1)*(3)+3-1];
        d[(3-1)*(3)+1-1]=e[(3-1)*(3)+1-1];
        d[(3-1)*(3)+2-1]=e[(3-1)*(3)+2-1];
        d[(3-1)*(3)+3-1]=e[(3-1)*(3)+3-1];
        dwave[(1-1)*(3)+1-1]=+d[(1-1)*(3)+1-1]+qrev[(1-1)*(3)+1-1]*dt;
        dwave[(1-1)*(3)+2-1]=+d[(1-1)*(3)+2-1]+qrev[(1-1)*(3)+2-1]*dt;
        dwave[(1-1)*(3)+3-1]=+d[(1-1)*(3)+3-1]+qrev[(1-1)*(3)+3-1]*dt;
        dwave[(2-1)*(3)+1-1]=+d[(2-1)*(3)+1-1]+qrev[(2-1)*(3)+1-1]*dt;
        dwave[(2-1)*(3)+2-1]=+d[(2-1)*(3)+2-1]+qrev[(2-1)*(3)+2-1]*dt;
        dwave[(2-1)*(3)+3-1]=+d[(2-1)*(3)+3-1]+qrev[(2-1)*(3)+3-1]*dt;
        dwave[(3-1)*(3)+1-1]=+d[(3-1)*(3)+1-1]+qrev[(3-1)*(3)+1-1]*dt;
        dwave[(3-1)*(3)+2-1]=+d[(3-1)*(3)+2-1]+qrev[(3-1)*(3)+2-1]*dt;
        dwave[(3-1)*(3)+3-1]=+d[(3-1)*(3)+3-1]+qrev[(3-1)*(3)+3-1]*dt;
        shearwave=1/shear+shearqrev*dt;
        det=invm(3,dwave,d);
        shearwave=1/shearwave;
        shear=shearwave;
        j = (num-1)*ngaus*7+(igaus-1)*7;
        for (i=1; i<=7; ++i) str[i]=inelmc8[j+i];
        e[(1-1)*(3)+1-1]=+coefc[(1-1)*(9)+1-1];
        e[(1-1)*(3)+2-1]=+coefc[(1-1)*(9)+2-1];
        e[(1-1)*(3)+3-1]=+coefc[(1-1)*(9)+3-1];
        e[(2-1)*(3)+1-1]=+coefc[(2-1)*(9)+1-1];
        e[(2-1)*(3)+2-1]=+coefc[(2-1)*(9)+2-1];
        e[(2-1)*(3)+3-1]=+coefc[(2-1)*(9)+3-1];
        e[(3-1)*(3)+1-1]=+coefc[(3-1)*(9)+1-1];
        e[(3-1)*(3)+2-1]=+coefc[(3-1)*(9)+2-1];
        e[(3-1)*(3)+3-1]=+coefc[(3-1)*(9)+3-1];
        dev[1]=e[(1-1)*(3)+1-1];
        dev[2]=e[(2-1)*(3)+2-1];
        dev[3]=e[(3-1)*(3)+3-1];
        dep[1] = e[(2-1)*(3)+3-1]+e[(3-1)*(3)+2-1];
        dep[2] = e[(1-1)*(3)+3-1]+e[(3-1)*(3)+1-1];
        dep[3] = e[(1-1)*(3)+2-1]+e[(2-1)*(3)+1-1];
        ds[1]=+d[(1-1)*(3)+1-1]*dev[1]+d[(1-1)*(3)+2-1]*dev[2]+d[(1-1)*(3)+3-1]*dev[3];
        ds[2]=+d[(2-1)*(3)+1-1]*dev[1]+d[(2-1)*(3)+2-1]*dev[2]+d[(2-1)*(3)+3-1]*dev[3];
        ds[3]=+d[(3-1)*(3)+1-1]*dev[1]+d[(3-1)*(3)+2-1]*dev[2]+d[(3-1)*(3)+3-1]*dev[3];
        ds[4]=shear*dep[1];
        ds[5]=shear*dep[2];
        ds[6]=shear*dep[3];
        ialpha=1;
        a=getyield(p,str,d,shear,ddf,kq,prager,ialpha);
        prag=prager(p,str);
        dln=ddf[1]*dev[1]+ddf[2]*dev[2]+ddf[3]*dev[3]
            +ddf[4]*dep[1]+ddf[5]*dep[2]+ddf[6]*dep[3]+prag;
        str[1]=str[1]+ds[1];
        str[2]=str[2]+ds[2];
        str[3]=str[3]+ds[3];
        str[4]=str[4]+ds[4];
        str[5]=str[5]+ds[5];
        str[6]=str[6]+ds[6];
        if (dln>0.0)
        {
            b=1.0/a;
            ds[1]=+b*ddg[1]*ddf[1]*dev[1]+b*ddg[1]*ddf[2]*dev[2]+b*ddg[1]*ddf[3]*dev[3];
            ds[2]=+b*ddg[2]*ddf[1]*dev[1]+b*ddg[2]*ddf[2]*dev[2]+b*ddg[2]*ddf[3]*dev[3];
            ds[3]=+b*ddg[3]*ddf[1]*dev[1]+b*ddg[3]*ddf[2]*dev[2]+b*ddg[3]*ddf[3]*dev[3];
            ds[4]=+b*ddg[4]*ddf[4]*dep[1];
            ds[5]=+b*ddg[5]*ddf[5]*dep[2];
            ds[6]=+b*ddg[6]*ddf[6]*dep[3];
            str[1]=+str[1]-ds[1]-ddg[1]*prag*b;
            str[2]=+str[2]-ds[2]-ddg[2]*prag*b;
            str[3]=+str[3]-ds[3]-ddg[3]*prag*b;
            str[4]=+str[4]-ds[4]-ddg[4]*prag*b;
            str[5]=+str[5]-ds[5]-ddg[5]*prag*b;
            str[6]=+str[6]-ds[6]-ddg[6]*prag*b;
        }
        else
        {
            b=0.0;
        }
        dsv1[(1-1)*(3)+1-1]=+d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]+d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]+d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1];
        dsv1[(1-1)*(3)+2-1]=+d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]+d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]+d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1];
        dsv1[(1-1)*(3)+3-1]=+d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]+d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]+d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1];
        dsv1[(2-1)*(3)+1-1]=+d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]+d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]+d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1];
        dsv1[(2-1)*(3)+2-1]=+d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]+d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]+d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1];
        dsv1[(2-1)*(3)+3-1]=+d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]+d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]+d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1];
        dsv1[(3-1)*(3)+1-1]=+d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]+d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]+d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1];
        dsv1[(3-1)*(3)+2-1]=+d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]+d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]+d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1];
        dsv1[(3-1)*(3)+3-1]=+d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]+d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]+d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1];
        ds[1]=+dsv1[(1-1)*(3)+1-1]*str[1]*dt+dsv1[(1-1)*(3)+2-1]*str[2]*dt+dsv1[(1-1)*(3)+3-1]*str[3]*dt;
        ds[2]=+dsv1[(2-1)*(3)+1-1]*str[1]*dt+dsv1[(2-1)*(3)+2-1]*str[2]*dt+dsv1[(2-1)*(3)+3-1]*str[3]*dt;
        ds[3]=+dsv1[(3-1)*(3)+1-1]*str[1]*dt+dsv1[(3-1)*(3)+2-1]*str[2]*dt+dsv1[(3-1)*(3)+3-1]*str[3]*dt;
        ds[4]=+shear*shearqrev*str[4]*dt;
        ds[5]=+shear*shearqrev*str[5]*dt;
        ds[6]=+shear*shearqrev*str[6]*dt;
        str[1]=+str[1]+ds[1];
        str[2]=+str[2]+ds[2];
        str[3]=+str[3]+ds[3];
        str[4]=+str[4]+ds[4];
        str[5]=+str[5]+ds[5];
        str[6]=+str[6]+ds[6];
        ialpha=1;
        a=getyield(p,str,d,shear,ddf,kq,prager,ialpha);
        prag=prager(p,str);
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
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+2-1]*ddf[1]+cu[(i-1)*(4)+4-1]*ddf[5]+cu[(i-1)*(4)+3-1]*ddf[6];
            eplast[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+3-1]*ddf[2]+cv[(i-1)*(4)+4-1]*ddf[4]+cv[(i-1)*(4)+2-1]*ddf[6];
            eplast[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+4-1]*ddf[3]+cw[(i-1)*(4)+3-1]*ddf[4]+cw[(i-1)*(4)+2-1]*ddf[5];
            eplast[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+2-1]*ddg[1]+cu[(i-1)*(4)+4-1]*ddg[5]+cu[(i-1)*(4)+3-1]*ddg[6];
            eplastg[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+3-1]*ddg[2]+cv[(i-1)*(4)+4-1]*ddg[4]+cv[(i-1)*(4)+2-1]*ddg[6];
            eplastg[iv]+=stif;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+4-1]*ddg[3]+cw[(i-1)*(4)+3-1]*ddg[4]+cw[(i-1)*(4)+2-1]*ddg[5];
            eplastg[iv]+=stif;
        }
// .... the following is the stiffness computation
        for (iv=1; iv<=24; ++iv)
        {
            for (jv=1; jv<=24; ++jv)
            {
                stif=+eexx[iv]*eexx[jv]*d[(1-1)*(3)+1-1]*vol
                     +eexx[iv]*eeyy[jv]*d[(1-1)*(3)+2-1]*vol
                     +eexx[iv]*eezz[jv]*d[(1-1)*(3)+3-1]*vol
                     +eeyy[iv]*eexx[jv]*d[(2-1)*(3)+1-1]*vol
                     +eeyy[iv]*eeyy[jv]*d[(2-1)*(3)+2-1]*vol
                     +eeyy[iv]*eezz[jv]*d[(2-1)*(3)+3-1]*vol
                     +eezz[iv]*eexx[jv]*d[(3-1)*(3)+1-1]*vol
                     +eezz[iv]*eeyy[jv]*d[(3-1)*(3)+2-1]*vol
                     +eezz[iv]*eezz[jv]*d[(3-1)*(3)+3-1]*vol
                     +eeyz[iv]*eeyz[jv]*shear*vol
                     +eexz[iv]*eexz[jv]*shear*vol
                     +eexy[iv]*eexy[jv]*shear*vol
                     -eplast[iv]*eplastg[jv]*b*vol;
                estif[(iv-1)*(24)+jv-1]=estif[(iv-1)*(24)+jv-1]+stif*weigh;
            }
        }
// .... the following is the load vector computation
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+1-1];
            stif=+cu[(i-1)*(4)+1-1]*fx*time1*vol;
            eload[iv]+=stif*weigh;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+2-1];
            stif=+cv[(i-1)*(4)+1-1]*fy*time1*vol;
            eload[iv]+=stif*weigh;
        }
        for (i=1; i<=8; ++i)
        {
            iv=kvord[(i-1)*(3)+3-1];
            stif=+cw[(i-1)*(4)+1-1]*fz*time1*vol;
            eload[iv]+=stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eexx[iv]*str[1]*vol+eexx[iv]*d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]*str[1]*dt+eexx[iv]*d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]*str[2]*dt+eexx[iv]*d[(1-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]*str[3]*dt+eexx[iv]*d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]*str[1]*dt+eexx[iv]*d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]*str[2]*dt+eexx[iv]*d[(1-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]*str[3]*dt+eexx[iv]*d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1]*str[1]*dt+eexx[iv]*d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1]*str[2]*dt+eexx[iv]*d[(1-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1]*str[3]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eeyy[iv]*str[2]*vol+eeyy[iv]*d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]*str[1]*dt+eeyy[iv]*d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]*str[2]*dt+eeyy[iv]*d[(2-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]*str[3]*dt+eeyy[iv]*d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]*str[1]*dt+eeyy[iv]*d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]*str[2]*dt+eeyy[iv]*d[(2-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]*str[3]*dt+eeyy[iv]*d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1]*str[1]*dt+eeyy[iv]*d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1]*str[2]*dt+eeyy[iv]*d[(2-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1]*str[3]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eezz[iv]*str[3]*vol+eezz[iv]*d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+1-1]*str[1]*dt+eezz[iv]*d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+2-1]*str[2]*dt+eezz[iv]*d[(3-1)*(3)+1-1]*qrev[(1-1)*(3)+3-1]*str[3]*dt+eezz[iv]*d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+1-1]*str[1]*dt+eezz[iv]*d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+2-1]*str[2]*dt+eezz[iv]*d[(3-1)*(3)+2-1]*qrev[(2-1)*(3)+3-1]*str[3]*dt+eezz[iv]*d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+1-1]*str[1]*dt+eezz[iv]*d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+2-1]*str[2]*dt+eezz[iv]*d[(3-1)*(3)+3-1]*qrev[(3-1)*(3)+3-1]*str[3]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eeyz[iv]*str[4]*vol+eeyz[iv]*shear*shearqrev*str[4]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eexz[iv]*str[5]*vol+eexz[iv]*shear*shearqrev*str[5]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=-eexy[iv]*str[6]*vol+eexy[iv]*shear*shearqrev*str[6]*dt;
            eload[iv]=eload[iv]+stif*weigh;
        }
        for (iv=1; iv<=24; ++iv)
        {
            stif=+eplastg[iv]*b*prag*vol-eplastg[iv]*b*ddf[1]*qrev[(1-1)*(3)+1-1]*str[1]*dt-eplastg[iv]*b*ddf[1]*qrev[(1-1)*(3)+2-1]*str[2]*dt-eplastg[iv]*b*ddf[1]*qrev[(1-1)*(3)+3-1]*str[3]*dt-eplastg[iv]*b*ddf[2]*qrev[(2-1)*(3)+1-1]*str[1]*dt-eplastg[iv]*b*ddf[2]*qrev[(2-1)*(3)+2-1]*str[2]*dt-eplastg[iv]*b*ddf[2]*qrev[(2-1)*(3)+3-1]*str[3]*dt-eplastg[iv]*b*ddf[3]*qrev[(3-1)*(3)+1-1]*str[1]*dt-eplastg[iv]*b*ddf[3]*qrev[(3-1)*(3)+2-1]*str[2]*dt-eplastg[iv]*b*ddf[3]*qrev[(3-1)*(3)+3-1]*str[3]*dt-eplastg[iv]*b*ddf[4]*shearqrev*str[4]*dt-eplastg[iv]*b*ddf[5]*shearqrev*str[5]*dt-eplastg[iv]*b*ddf[6]*shearqrev*str[6]*dt;
            eload[iv]=eload[iv]+stif*weigh;
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

static void coef_shap(double *refc,double *coef,double *coefr,double *coefd)
/* compute coef value and their partial derivatives
by reference coordinate value */
{
    double (*shap)(double *,int)=&fcoef_shap;
// extern void dcoef(shap,double *,double *,double *,
//  int,int,int);
    dcoef(shap,refc,coef,coefd,3,3,2);
    /* coef value and their partial derivatives caculation
     compute partial derivatives by centered difference
     which is in the file cshap.c of felac library */
    return;
}

static double fcoef_shap(double *refc,int n)
/* coef function caculation */
{
    double rx,ry,rz;
    double x,y,z,fval;
    double un[9],vn[9],wn[9];
    int j;
    for (j=1; j<=8; ++j)
    {
        un[j]=coefr[(1-1)*(8)+j-1];
        vn[j]=coefr[(2-1)*(8)+j-1];
        wn[j]=coefr[(3-1)*(8)+j-1];
    }
    x=coor[1];
    y=coor[2];
    z=coor[3];
    rx=refc[1];
    ry=refc[2];
    rz=refc[3];
    switch (n)
    {
    case 1:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*un[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*un[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*un[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*un[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*un[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*un[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*un[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*un[8];
        break;
    case 2:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*vn[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*vn[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*vn[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*vn[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*vn[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*vn[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*vn[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*vn[8];
        break;
    case 3:
        fval=
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*wn[1]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.-rz)/2.)*wn[2]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*wn[3]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.-rz)/2.)*wn[4]
            +(+(+1.-rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*wn[5]
            +(+(+1.+rx)/2.*(+1.-ry)/2.*(+1.+rz)/2.)*wn[6]
            +(+(+1.+rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*wn[7]
            +(+(+1.-rx)/2.*(+1.+ry)/2.*(+1.+rz)/2.)*wn[8];
        break;
        //default:
    }
    return fval;
}

