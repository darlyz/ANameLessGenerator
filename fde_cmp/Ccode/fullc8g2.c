#include "felac.h"
double nx,ny,nz;
int nnode,ngaus,ndisp,nrefc,ncoor,nvar;
double vol,det,weigh,stif,fact,shear,r0;
int nvard[9],kdord[9],kvord[576];
double refc[24],gaus[9];
double coor[4];
double coorr[24];
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
static void shap_Axr(double *,double *);
static double fshap_Axr(double *,int);
static void shap_Axi(double *,double *);
static double fshap_Axi(double *,int);
static void shap_Ayr(double *,double *);
static double fshap_Ayr(double *,int);
static void shap_Ayi(double *,double *);
static double fshap_Ayi(double *,int);
static void shap_Azr(double *,double *);
static double fshap_Azr(double *,int);
static void shap_Azi(double *,double *);
static double fshap_Azi(double *,int);
static void shap_phir(double *,double *);
static double fshap_phir(double *,int);
static void shap_phii(double *,double *);
static double fshap_phii(double *,int);
void shapn(int,int,int,double *,double *,double *,int,int,int);
void shapc(int,int,int,double *,double *,double *,int,int,int);
void fullc8g2(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)
double coora[24],*coefa,*prmt,estif[576],*emass,*edamp,*eload;
int num,ibegin;
{
	double refcoor[4]= {0.0,0.0,0.0,0.0};
	double ecurlAxr[25],ecurlAxi[25],ecurlAyr[25],ecurlAyi[25],ecurlAzr[25],ecurlAzi[25],edivAr[25],edivAi[25],ephixr[25],ephixi[25],ephiyr[25],ephiyi[25],ephizr[25],ephizi[25],eVBxr[25],eVBxi[25],eVByr[25],eVByi[25],eVBzr[25],eVBzi[25];
	double x,y,z,rx,ry,rz;
	double elump[25];
	static double rAxr[256],rAxi[256],rAyr[256],rAyi[256],rAzr[256],rAzi[256],rphir[256],rphii[256],cAxr[32],cAxi[32],cAyr[32],cAyi[32],cAzr[32],cAzi[32],cphir[32],cphii[32];
	int i,j,igaus;
	int ig_Axr,ig_Axi,ig_Ayr,ig_Ayi,ig_Azr,ig_Azi,ig_phir,ig_phii,iv,jv;
double Dremxr,Dremxi,Dremyr;

double Dremyi,Dremzr,Dremzi;

double Bremxr,Bremxi,Bremyr;

double Bremyi,Bremzr,Bremzi;

double Jexr,  Jeyr,  Jezr;

double Jexi,  Jeyi,  Jezi;

double Pxr,   Pyr,   Pzr;

double Pxi,   Pyi,   Pzi;

double Mxr,   Myr,   Mzr;

double Mxi,   Myi,   Mzi;

double sgm11,sgm12,sgm13;

double sgm21,sgm22,sgm23;

double sgm31,sgm32,sgm33;

double ep11r,ep12r,ep13r;

double ep21r,ep22r,ep23r;

double ep31r,ep32r,ep33r;

double ep11i,ep12i,ep13i;

double ep21i,ep22i,ep23i;

double ep31i,ep32i,ep33i;

double mu11r,mu12r,mu13r;

double mu21r,mu22r,mu23r;

double mu31r,mu32r,mu33r;

double mu11i,mu12i,mu13i;

double mu21i,mu22i,mu23i;

double mu31i,mu32i,mu33i;

double mur,epr,sigma;

double fHz,omega,pc;

double Vx,Vy,Vz;

double pi  = 3.14159265358979;

double ep0 = 8.854187817e-12;

double mu0 = 4*pi*1e-7;

double Jetag=1;

if (Jetag!=0) Jetag=1;

	mur=prmt[1];
	epr=prmt[2];
	sigma=prmt[3];
	fHz=prmt[4];
	Jexr=prmt[5];
	Jexi=prmt[6];
	Jeyr=prmt[7];
	Jeyi=prmt[8];
	Jezr=prmt[9];
	Jezi=prmt[10];
	Vx=prmt[11];
	Vy=prmt[12];
	Vz=prmt[13];
	pc=prmt[14];
	if (num==ibegin) initial();
	for (i=1; i<=3; ++i)
	    for (j=1; j<=8; ++j)
	        coorr[(i-1)*(8)+j-1]=coora[(i-1)*(8)+j-1];
	for (i=1; i<=64; ++i)
	{
	    eload[i]=0.0;
	    for (j=1; j<=64; ++j)
	    {
	        estif[(i-1)*(64)+j-1]=0.0;
	    }
	}
	for (igaus=1; igaus<=ngaus; ++igaus)
	{
	    for (i=1; i<=nrefc; ++i)
			refcoor[i]=refc[(i-1)*(8)+igaus-1];
	    tran_coor(refcoor,coor,coorr,rctr);
		// det = invm(ncoor,rctr,crtr);
		det = inver_rc(nrefc,ncoor,rctr,crtr);
		x=coor[1];
		y=coor[2];
		z=coor[3];
		rx=refcoor[1];
		ry=refcoor[2];
		rz=refcoor[3];
		ig_Axr=(igaus-1)*8*4;
		ig_Axi=(igaus-1)*8*4;
		ig_Ayr=(igaus-1)*8*4;
		ig_Ayi=(igaus-1)*8*4;
		ig_Azr=(igaus-1)*8*4;
		ig_Azi=(igaus-1)*8*4;
		ig_phir=(igaus-1)*8*4;
		ig_phii=(igaus-1)*8*4;
		if (num>ibegin)
			goto l2;
		shap_Axr(refcoor,&rAxr[ig_Axr]);
		shap_Axi(refcoor,&rAxi[ig_Axi]);
		shap_Ayr(refcoor,&rAyr[ig_Ayr]);
		shap_Ayi(refcoor,&rAyi[ig_Ayi]);
		shap_Azr(refcoor,&rAzr[ig_Azr]);
		shap_Azi(refcoor,&rAzi[ig_Azi]);
		shap_phir(refcoor,&rphir[ig_phir]);
		shap_phii(refcoor,&rphii[ig_phii]);
l2:		shapn(nrefc,ncoor,8,&rAxr[ig_Axr],cAxr,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rAxi[ig_Axi],cAxi,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rAyr[ig_Ayr],cAyr,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rAyi[ig_Ayi],cAyi,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rAzr[ig_Azr],cAzr,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rAzi[ig_Azi],cAzi,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rphir[ig_phir],cphir,crtr,1,4,4);
		shapn(nrefc,ncoor,8,&rphii[ig_phii],cphii,crtr,1,4,4);
		weigh=det*gaus[igaus];
		for (i=1; i<=64; ++i)
		{
			ecurlAxr[i] = 0.0;
			ecurlAxi[i] = 0.0;
			ecurlAyr[i] = 0.0;
			ecurlAyi[i] = 0.0;
			ecurlAzr[i] = 0.0;
			ecurlAzi[i] = 0.0;
			edivAr[i] = 0.0;
			edivAi[i] = 0.0;
			ephixr[i] = 0.0;
			ephixi[i] = 0.0;
			ephiyr[i] = 0.0;
			ephiyi[i] = 0.0;
			ephizr[i] = 0.0;
			ephizi[i] = 0.0;
			eVBxr[i] = 0.0;
			eVBxi[i] = 0.0;
			eVByr[i] = 0.0;
			eVByi[i] = 0.0;
			eVBzr[i] = 0.0;
			eVBzi[i] = 0.0;
		}
