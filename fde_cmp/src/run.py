import os
import re
from sys import argv,exit

dirs = os.listdir("../0xde_source/all_fde")

out_put = 0

def ex2file(xdename,xde_name,shap,dim,axi):
    if out_put == 1:
        file = open("run.log",mode='a')
        file.write(f"parsing {xdename} to {xde_name}{shap}\n")
        file.close()
        os.system(f"genxde ../0xde_source/all_fde/{xdename} {xde_name}{shap} {dim}{axi} >> run.log")
        file = open("run.log",mode='a')
        file.write('-'*128+'\n')
        file.close()
    elif out_put == 0:
        print(f"parsing {xdename} to {xde_name}{shap}\n")
        os.system(f"genxde ../0xde_source/all_fde/{xdename} {xde_name}{shap} {dim}{axi}")
        print('-'*128+'\n')

def main(argvs=None):
    if argvs is None:
        argvs = argv
        
    global out_put
    if len(argvs) == 2 and argvs[1] == '-log':
        out_put = 1
    else:
        out_put = 0
    
    if out_put == 1:
        os.system("del run.log")

    for xdename in dirs:
        xde_name, pos_name = xdename.split('.')
        
        if re.search(r'xyz|roz|rso', xdename, re.I) != None:
            axi = re.search(r'xyz|roz|rso', xdename, re.I).group()
            
            #for shap in ['w4g2','c8g2','w10g3','c27g3']:
            for shap in ['w4g2']:
                ex2file(xdename,xde_name,shap,'3d',axi)
    
        elif re.search(r'xy|r[soz]|so', xdename, re.I) != None:
            axi = re.search(r'xy|r[soz]|so', xdename, re.I).group()
                
            #for shap in ['t3g2','q4g2','t6g3','q9g3']:
            for shap in ['t3g2']:
                ex2file(xdename,xde_name,shap,'2d',axi)
                
        elif re.search(r'x|r|s', xdename, re.I) != None:
            axi = re.search(r'x|r|s', xdename, re.I).group()
            
            #for shap in ['l2g2','l3g3']:
            for shap in ['l2g2']:
                ex2file(xdename,xde_name,shap,'1d',axi)
            
    #print('-'*128)

if __name__ == "__main__":
    exit(main())
