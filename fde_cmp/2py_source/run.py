import os
import re as regx

dirs = os.listdir("../0xde_source/all_fde")

out_put = 1

if out_put == 1:
	os.system("del run.log")

def ex2file(xdename,xde_name,shap,dim,axi):
	if out_put == 1:
		file = open("run.log",mode='a')
		file.write(f"parsing {xdename} to {xde_name}{shap}\n")
		file.close()
		os.system(f"python genxde.py all_fde/{xdename} {xde_name}{shap} {dim}{axi} >> run.log")
		file = open("run.log",mode='a')
		file.write('-'*128+'\n')
		file.close()
	elif out_put == 0:
		print(f"parsing {xdename} to {xde_name}{shap}\n")
		os.system(f"python genxde.py all_fde/{xdename} {xde_name}{shap} {dim}{axi}")
		print('-'*128+'\n')


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