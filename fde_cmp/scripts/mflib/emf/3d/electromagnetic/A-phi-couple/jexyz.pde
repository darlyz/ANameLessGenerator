disp jx jy jz jxr jyr jzr jxi jyi jzi
coef axr axi ayr ayi azr azi ur ui
coor x y z
shap %1 %2
gaus %3
$cc double omega,sigma,sym_form;
$cc double guxr,guyr,guzr,guxi,guyi,guzi,exr,eyr,ezr,exi,eyi,ezi;
$cc double signjx,signjy,signjz;
$cc double ex,ey,ez;
$cc sym_form=0; // symmetric weak form when sym_form is not 0
mate omega sigma 12.56637e2 3.526e7
mass %1 vol vol vol vol vol vol vol vol vol
 
func
$cc vol = 1.0;
$cv guxr=+{ur/x}
$cv guyr=+{ur/y}
$cv guzr=+{ur/z}
$cv guxi=+{ui/x}
$cv guyi=+{ui/y}
$cv guzi=+{ui/z}
 
stif
$cc if(sym_form==0){
$cc   exr = -guxr+omega*axi;        exi = -guxi-omega*axr;
$cc   eyr = -guyr+omega*ayi;        eyi = -guyi-omega*ayr;
$cc   ezr = -guzr+omega*azi;        ezi = -guzi-omega*azr;
$cc }
$cc else{
$cc   exr = +omega*guxi+omega*axi;  exi = -omega*guxr-omega*axr;
$cc   eyr = +omega*guyi+omega*ayi;  eyi = -omega*guyr-omega*ayr;
$cc   ezr = +omega*guzi+omega*azi;  ezi = -omega*guzr-omega*azr;
$cc }
$cc if(exr>=0)      // jx
$cc    signjx=1.0;
$cc else
$cc    signjx=-1.0;
$cc if(eyr>=0)      // jy
$cc    signjy=1.0;
$cc else
$cc    signjy=-1.0;
$cc if(ezr>=0)      // jz
$cc    signjz=1.0;
$cc else
$cc    signjz=-1.0;
$cc ex=signjx*sqrt(exr*exr+exi*exi);
$cc ey=signjy*sqrt(eyr*eyr+eyi*eyi);
$cc ez=signjz*sqrt(ezr*ezr+ezi*ezi);
dist=+[jx;jx]*0
 
load=+[jx]*vol*sigma*ex
+[jy]*vol*sigma*ey
+[jz]*vol*sigma*ez
+[jxr]*vol*sigma*exr
+[jyr]*vol*sigma*eyr
+[jzr]*vol*sigma*ezr
+[jxi]*vol*sigma*exi
+[jyi]*vol*sigma*eyi
+[jzi]*vol*sigma*ezi
 
end
 
