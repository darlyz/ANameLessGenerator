import os
import re as regx
from sys import argv,exit
from genxde import genxde
from felac_data import get_felac_data

dirs = os.listdir("../0xde_source/all_fde")

get_felac_data()

def ex2file(xdename,xde_name,shap,dim,axi):
    import check_xde
    check_xde.error = False
    print(f"parsing {xdename} to {xde_name}{shap}\n")
    genxde(f'all_fde/{xdename}', xde_name+shap, dim+axi)
    print('-'*128+'\n')

def main(argvs=None):
    if argvs is None:
        argvs = argv

    if len(argvs) == 2 and argvs[1] == '-log':
        out_put = 1
    else:
        out_put = 0
    
    if out_put == 1:
        os.system("del run.log")

    for xdename in dirs:
        xde_name, pos_name = xdename.split('.')

        if regx.search(r'xyz|roz|rso', xdename, regx.I) != None:
            axi = regx.search(r'xyz|roz|rso', xdename, regx.I).group()

            #for shap in ['w4g2','c8g2','w10g3','c27g3']:
            for shap in ['w4g2']:
                ex2file(xdename,xde_name,shap,'3d',axi)

        elif regx.search(r'xy|r[soz]|so', xdename, regx.I) != None:
            axi = regx.search(r'xy|r[soz]|so', xdename, regx.I).group()

            #for shap in ['t3g2','q4g2','t6g3','q9g3']:
            for shap in ['t3g2']:
                ex2file(xdename,xde_name,shap,'2d',axi)

        elif regx.search(r'x|r|s', xdename, regx.I) != None:
            axi = regx.search(r'x|r|s', xdename, regx.I).group()

            #for shap in ['l2g2','l3g3']:
            for shap in ['l2g2']:
                ex2file(xdename,xde_name,shap,'1d',axi)
            
        #print('-'*128)

if __name__ == "__main__":
    exit(main())