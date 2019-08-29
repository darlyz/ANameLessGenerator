#include "felac.h"
double nx,ny,nz;
int nnode,ngaus,ndisp,nrefc,ncoor,nvar;
double vol,det,weigh,stif,fact,shear,r0;
int nvard[4],kdord[4],kvord[243];
double refc[81],gaus[28];
double coor[4];
double coorr[81];
double rctr[9],crtr[9];
void dshap(double (*shap)(double *,int),
       double *,double *,int,int,int);
void dcoor(double (*shap)(double *,int),
           double *,double *,double *,int,int,int);
double invm(int,double *,double *);
double inver_rc(int,int,double *,double *);
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
void aec27g3(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)
double coora[81],*coefa,*prmt,estif[6561],*emass,*edamp,*eload;
int num,ibegin;
{
	double refcoor[4]= {0.0,0.0,0.0,0.0};
	double eexx[82],eeyy[82],eezz[82],eeyz[82],eexz[82],eexy[82];
	double x,y,z,rx,ry,rz;
	double elump[82];
	static double ru[2916],rv[2916],rw[2916],cu[108],cv[108],cw[108];
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
	if (num==ibegin) initial();
	for (i=1; i<=3; ++i)
	    for (j=1; j<=27; ++j)
	        coorr[(i-1)*(27)+j-1]=coora[(i-1)*(27)+j-1];
	for (i=1; i<=81; ++i)
	{
	    eload[i]=0.0;
	    for (j=1; j<=81; ++j)
	    {
	        estif[(i-1)*(81)+j-1]=0.0;
	    }
	}
	for (igaus=1; igaus<=ngaus; ++igaus)
	{
	    for (i=1; i<=nrefc; ++i)
			refcoor[i]=refc[(i-1)*(27)+igaus-1];
	    tran_coor(refcoor,coor,coorr,rctr);
		// det = invm(ncoor,rctr,crtr);
		det = inver_rc(nrefc,ncoor,rctr,crtr);
		x=coor[1];
		y=coor[2];
		z=coor[3];
		rx=refcoor[1];
		ry=refcoor[2];
		rz=refcoor[3];
		ig_u=(igaus-1)*27*4;
		ig_v=(igaus-1)*27*4;
		ig_w=(igaus-1)*27*4;
		if (num>ibegin)
			goto l2;
		shap_u(refcoor,&ru[ig_u]);
		shap_v(refcoor,&rv[ig_v]);
		shap_w(refcoor,&rw[ig_w]);
l2:		shapn(nrefc,ncoor,27,&ru[ig_u],cu,crtr,1,4,4);
		shapn(nrefc,ncoor,27,&rv[ig_v],cv,crtr,1,4,4);
		shapn(nrefc,ncoor,27,&rw[ig_w],cw,crtr,1,4,4);
		weigh=det*gaus[igaus];
		for (i=1; i<=81; ++i)
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
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+1-1];
		    stif=+cu[(i-1)*(4)+2-1];
		    eexx[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+2-1];
		    stif=+cv[(i-1)*(4)+3-1];
		    eeyy[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+3-1];
		    stif=+cw[(i-1)*(4)+4-1];
		    eezz[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+2-1];
		    stif=+cv[(i-1)*(4)+4-1];
		    eeyz[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+3-1];
		    stif=+cw[(i-1)*(4)+3-1];
		    eeyz[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+1-1];
		    stif=+cu[(i-1)*(4)+4-1];
		    eexz[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+3-1];
		    stif=+cw[(i-1)*(4)+2-1];
		    eexz[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+1-1];
		    stif=+cu[(i-1)*(4)+3-1];
		    eexy[iv]+=stif;
		}
		for (i=1; i<=27; ++i)
		{
		    iv=kvord[(i-1)*(3)+2-1];
		    stif=+cv[(i-1)*(4)+2-1];
		    eexy[iv]+=stif;
		}
		stif=rou*alpha;
		elump[1]=stif*weight;
		stif=rou*alpha;
		elump[4]=stif*weight;
		stif=rou*alpha;
		elump[7]=stif*weight;
		stif=rou*alpha;
		elump[10]=stif*weight;
		stif=rou*alpha;
		elump[13]=stif*weight;
		stif=rou*alpha;
		elump[16]=stif*weight;
		stif=rou*alpha;
		elump[19]=stif*weight;
		stif=rou*alpha;
		elump[22]=stif*weight;
		stif=rou*alpha;
		elump[25]=stif*weight;
		stif=rou*alpha;
		elump[28]=stif*weight;
		stif=rou*alpha;
		elump[31]=stif*weight;
		stif=rou*alpha;
		elump[34]=stif*weight;
		stif=rou*alpha;
		elump[37]=stif*weight;
		stif=rou*alpha;
		elump[40]=stif*weight;
		stif=rou*alpha;
		elump[43]=stif*weight;
		stif=rou*alpha;
		elump[46]=stif*weight;
		stif=rou*alpha;
		elump[49]=stif*weight;
		stif=rou*alpha;
		elump[52]=stif*weight;
		stif=rou*alpha;
		elump[55]=stif*weight;
		stif=rou*alpha;
		elump[58]=stif*weight;
		stif=rou*alpha;
		elump[61]=stif*weight;
		stif=rou*alpha;
		elump[64]=stif*weight;
		stif=rou*alpha;
		elump[67]=stif*weight;
		stif=rou*alpha;
		elump[70]=stif*weight;
		stif=rou*alpha;
		elump[73]=stif*weight;
		stif=rou*alpha;
		elump[76]=stif*weight;
		stif=rou*alpha;
		elump[79]=stif*weight;
		stif=rou*alpha;
		elump[2]=stif*weight;
		stif=rou*alpha;
		elump[5]=stif*weight;
		stif=rou*alpha;
		elump[8]=stif*weight;
		stif=rou*alpha;
		elump[11]=stif*weight;
		stif=rou*alpha;
		elump[14]=stif*weight;
		stif=rou*alpha;
		elump[17]=stif*weight;
		stif=rou*alpha;
		elump[20]=stif*weight;
		stif=rou*alpha;
		elump[23]=stif*weight;
		stif=rou*alpha;
		elump[26]=stif*weight;
		stif=rou*alpha;
		elump[29]=stif*weight;
		stif=rou*alpha;
		elump[32]=stif*weight;
		stif=rou*alpha;
		elump[35]=stif*weight;
		stif=rou*alpha;
		elump[38]=stif*weight;
		stif=rou*alpha;
		elump[41]=stif*weight;
		stif=rou*alpha;
		elump[44]=stif*weight;
		stif=rou*alpha;
		elump[47]=stif*weight;
		stif=rou*alpha;
		elump[50]=stif*weight;
		stif=rou*alpha;
		elump[53]=stif*weight;
		stif=rou*alpha;
		elump[56]=stif*weight;
		stif=rou*alpha;
		elump[59]=stif*weight;
		stif=rou*alpha;
		elump[62]=stif*weight;
		stif=rou*alpha;
		elump[65]=stif*weight;
		stif=rou*alpha;
		elump[68]=stif*weight;
		stif=rou*alpha;
		elump[71]=stif*weight;
		stif=rou*alpha;
		elump[74]=stif*weight;
		stif=rou*alpha;
		elump[77]=stif*weight;
		stif=rou*alpha;
		elump[80]=stif*weight;
		stif=rou*alpha;
		elump[3]=stif*weight;
		stif=rou*alpha;
		elump[6]=stif*weight;
		stif=rou*alpha;
		elump[9]=stif*weight;
		stif=rou*alpha;
		elump[12]=stif*weight;
		stif=rou*alpha;
		elump[15]=stif*weight;
		stif=rou*alpha;
		elump[18]=stif*weight;
		stif=rou*alpha;
		elump[21]=stif*weight;
		stif=rou*alpha;
		elump[24]=stif*weight;
		stif=rou*alpha;
		elump[27]=stif*weight;
		stif=rou*alpha;
		elump[30]=stif*weight;
		stif=rou*alpha;
		elump[33]=stif*weight;
		stif=rou*alpha;
		elump[36]=stif*weight;
		stif=rou*alpha;
		elump[39]=stif*weight;
		stif=rou*alpha;
		elump[42]=stif*weight;
		stif=rou*alpha;
		elump[45]=stif*weight;
		stif=rou*alpha;
		elump[48]=stif*weight;
		stif=rou*alpha;
		elump[51]=stif*weight;
		stif=rou*alpha;
		elump[54]=stif*weight;
		stif=rou*alpha;
		elump[57]=stif*weight;
		stif=rou*alpha;
		elump[60]=stif*weight;
		stif=rou*alpha;
		elump[63]=stif*weight;
		stif=rou*alpha;
		elump[66]=stif*weight;
		stif=rou*alpha;
		elump[69]=stif*weight;
		stif=rou*alpha;
		elump[72]=stif*weight;
		stif=rou*alpha;
		elump[75]=stif*weight;
		stif=rou*alpha;
		elump[78]=stif*weight;
		stif=rou*alpha;
		elump[81]=stif*weight;
		for (i=1; i<=nvard[1]; ++i)
		{
		    iv = kvord[(i-1)*(3)+1-1];
		    edamp[iv]+=elump[iv]*cu[(i-1)*(4)+1-1];
		}
		for (i=1; i<=nvard[2]; ++i)
		{
		    iv = kvord[(i-1)*(3)+2-1];
		    edamp[iv]+=elump[iv]*cv[(i-1)*(4)+1-1];
		}
		for (i=1; i<=nvard[3]; ++i)
		{
		    iv = kvord[(i-1)*(3)+3-1];
		    edamp[iv]+=elump[iv]*cw[(i-1)*(4)+1-1];
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+1-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+1-1];
		        stif=+cu[(i-1)*3+1-1]*cu[(i-1)*3+1-1]*rou;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+2-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+2-1];
		        stif=+cv[(i-1)*3+1-1]*cv[(i-1)*3+1-1]*rou;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+3-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+3-1];
		        stif=+cw[(i-1)*3+1-1]*cw[(i-1)*3+1-1]*rou;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+1-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+2-1];
		        stif=+cu[(i-1)*3+1-1]*cv[(i-1)*3+1-1]*1;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+2-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+3-1];
		        stif=+cv[(i-1)*3+2-1]*cw[(i-1)*3+3-1]*2
		             +cv[(i-1)*3+1-1]*cw[(i-1)*3+4-1]*3;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		{
		    iv=kvord[(i-1)*3+3-1];
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+1-1];
		        stif=+cw[(i-1)*3+1-1]*cu[(i-1)*3+2-1]*4;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (i=1; i<=81; ++i)
		
		    iv=kvord[(i-1)*3+1-1];
		    for (jv=1; jv<=81; ++jv)
		    {
		        stif=+cu[(i-1)*(3)+1-1]*eux[jv]*2
		             +cu[(i-1)*(3)+3-1]*euy[jv]*8;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (iv=1; iv<=81; ++iv)
		{
		    for (j=1; j<=81; ++j)
		    {
		        jv=kvord[(j-1)*3+1-1];
		        stif=+euy[iv]*cu[(j-1)*(3)+1-1]*3
		             +eux[iv]*cu[(j-1)*(3)+3-1]*7;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (iv=1; iv<=81; ++iv)
		{
		    for (jv=1; jv<=81; ++jv)
		    {
		        stif=+eux[iv]*eux[jv]*vol*epsilon
		             +euy[iv]*euy[jv]*vol*epsilon;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
		for (iv=1; iv<=81; ++iv)
		{
		    for (jv=1; jv<=81; ++jv)
		    {
		        stif=+eux[iv]*eux[jv]*vol*epsilon
		             +euy[iv]*euy[jv]*vol*epsilon;
		        estif[(iv-1)*81+jv-1]+=stif*weigh;
		    }
		}
