#include "math.h"
void samar(rflux,rr,emu,mode)
int mode;
double rflux,emu;
double *rr;
{
    double tiny,rz,temp;
    tiny = 1.e-30;
    rz = rflux/(emu+tiny);
    switch(mode)
    {
    case 1:
        if (rz>=0.)
        {
            *rr=(1.+rz)/(2.+rz);
        }
        else
        {
            *rr=1./(2.-rz);
        }
        break;
    case 2:
        if (rz>tiny)
        {
            *rr = 1.;
        }
        else
        {
            *rr = 0.;
        }
        break;
    case 3:
        if (rz>tiny)
        {
            *rr = 1.-1./rz+1./(exp(rz)-1.);
        }
        else
        {
            *rr = -1./rz-1./(exp(-rz)-1.);
        }
        break;
    case 4:
        temp = exp(rz)*exp(rz);
        *rr = 0.5*(1.+(temp-1.)/(temp+1.));
        break;
    default:
        /*        print*,'error!';
                print*,'please make sure the value of mode is valiable.';
                print*,'you have 4 choices:';
                print*,'mode = 1...........samarskij';
                print*,'mode = 2...........0-1 scheme';
                print*,'mode = 3...........exponentially fitted scheme';
                print*,'mode = 4...........tanh function' ;
                pause;
         */
        break;
    }
    return;
// ... ........................................
}
