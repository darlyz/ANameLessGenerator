'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: main func of generate xde file to ges
 All rights reserved
'''
from sys import argv,exit
from time import time

# ...$python genfde.py filename elemtype		
def main(argvs=None):
	if argvs is None:
		argvs = argv
	
	start = time()
	
	keyws_reg  = 'DISP|COEF|COOR|SHAP|GAUS|MATE|MASS|DAMP|STIF|'
	keyws_reg += 'FUNC|VECT|MATRIX|FVECT|FMATR|ARRAY|DIST|LOAD|END|'
	keyws_reg += '\$C[CPV]|@[LAWSR]'
	keywd_tag = {'disp':0, 'coor':0, 'shap':0 , 'gaus':0  , 'mate':0, 'mass':0, 'damp':0, 'stif':0, 'coef':0, 'load':0, \
				'vect':0, 'fvect':0, 'func':0, 'fmatr':0, 'matrix':0, \
				'code':{'BFmate':0, 'AFmate':0, 'dolrI':0, 'INfunc':0, 'INstif':0, 'INmass':0, 'INdamp':0, }, 
				'dist':'', 'masstype':0, 'damptype':0, 'stiftype':0, 'matrixname':'','matrixtag':0, 'complex':0}
	list_addr = {}
	list_addr['code'] = {}
	list_addr['code']['BFmate'] = []
	list_addr['code']['AFmate'] = []
	list_addr['code']['func'] = []
	list_addr['code']['stif'] = []
	list_addr['code']['mass'] = []
	list_addr['code']['damp'] = []
	xde_lists = {}
	xde_lists['code'] = {}
	xde_lists['code']['BFmate'] = []
	xde_lists['code']['AFmate'] = []
	xde_lists['code']['func'] = []
	xde_lists['code']['stif'] = []
	xde_lists['code']['mass'] = []
	xde_lists['code']['damp'] = []

	from parse_xde import parse_xde
	parse_xde(argvs[1],argvs[2],argvs[3],keywd_tag,xde_lists,list_addr,keyws_reg)
	
	#print(xde_lists)
	#for ll in xde_lists.keys():
	#	print(ll,xde_lists[ll])
	#for ll in list_addr.keys():
	#	print(ll,list_addr[ll])
	
	#from xde2ges import xde2ges
	#xde2ges(argvs[2],keywd_tag,xde_lists,list_addr,keyws_reg,argvs[3])
	
	end   = time()
	print ('parsing time: {}s'.format(end-start))
	
	import json
	file = open(argvs[2]+'.json',mode='w')
	file.write(json.dumps(xde_lists,indent=4))
	file.close()
	
	
if __name__ == "__main__":
	exit(main())