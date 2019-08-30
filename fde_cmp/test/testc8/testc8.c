/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = testc8.c
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
int gidpre(void);
int gidmsh(struct coordinates,struct element);
int gidres(struct coordinates);
void starta(struct coordinates,int,int *,double *,struct element, struct matrice *, double **);
void etestc8a(struct coordinates,int,int *,double *,struct element,struct matrice,double *);
void solv(struct matrice,double *);
void utestc8a(struct coordinates,int,int *,double *,double *);
int main (int argc, char *args[])
{
    if(argc>1)
    {
        if((!strcmp(args[1],"-version"))||(!strcmp(args[1],"-v")))
        {
            printf("version:3.0\n");
            printf("Time of release:2019-08-30 13:13:40\n");
            printf("The Code GenID is:\n");
            printf("22565914_000906e9061008007ffafbffbfebfbff_005056c00001\n");
            return 1;
        }
    }
    gidpre();
    gidmsh(coor0,elema);
    starta(coor0,dofa,ida,ubfa,elema,&matrixa,&fa);
    setsolver(default_solver,default_solvpara);
    etestc8a(coor0,dofa,ida,ubfa,elema,matrixa,fa);
    solv(matrixa,fa);
    utestc8a(coor0,dofa,ida,ubfa,fa);
    gidres(coor0);
}
