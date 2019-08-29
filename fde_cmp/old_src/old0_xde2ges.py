'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the jason data to ges file
 All rights reserved
'''
import re as regx
import os

def release_BF_AF_mate_code(fdelist,AFBFmate,file,pfelacpath,singular_list):
	for strs in fdelist['code'][AFBFmate]:
			regxrp = regx.search('\$CC|\$CP|\$CV|@L|@W|@A',strs,regx.I)
			
			if regxrp.group().lower() == '$cc': # <------- could add the function of checking mate variable
				file.write(strs+'\n')
			
			elif regxrp.group().lower() == '@l':
				singular_expr = ''
				singular_find = 0
				regxrp_singular = regx.search('singular',strs,regx.I)
				path_opr = pfelacpath+'ges\\pde.lib'
				file_opr = open(path_opr, mode='r')
				coor_true = ''
				
				for ww in fdelist['coor']: coor_true += ww
				if regxrp_singular != None:
					singular_expr = strs.split()[1]
					coor_exp = singular_expr.split('.')[1]
					if coor_exp != coor_true:
						print('warning: make sure that singular operator is \'{}\' but not \'singular.{}\'.'.format(singular_expr,coor_true))
				else :
					print('warning: valid operator is only \'singular\' before mate declaration.')
					continue
				#else: # <------- need to add the function of auto-add singular operation
				#	print('warning: not found operator \'singular\', auto-added by \'singular.{}\'.'.format(coor_true))
				#	print('!!!!!!!!!!!!')
				#	singular_expr = 'singular.'+coor_true
				
				for line in file_opr.readlines():
					singular_start_file = regx.search('sub '+singular_expr,line,regx.I)
					singular_end_file   = regx.search('end '+singular_expr,line,regx.I)
					if singular_start_file != None:
						singular_find = 1
						continue
					if singular_end_file   != None:
						singular_find = 0
						continue
					if singular_find == 1:
						singular_list.append(line)
				
				file_opr.close()
				
			elif regxrp.group().lower() == '$cv': # <------- need to add function
				pass
			elif regxrp.group().lower() == '$cp': # <------- need to add function
				pass
			else:
				print('warning: \'@W\' and \'@A\' are invalid before mate declaration.')


def xde2ges(gesname,list,keywdtag,fdelist,regkeyws):

	#gesname = 'aec8g2'
	shap_tag1 = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
	shap_tag2 = regx.search(r'g[1-9]+',gesname,regx.I)
	if shap_tag2 != None:
		shap_tag2 = shap_tag2.group()
	
	file = open(gesname+'.ges1', mode='w')
	file.write(gesname+'\ndefi\n')
	
	pfelacpath = os.environ['pfelacpath']

	# write disp and var declare
	if fdelist['disp'] != None:
		file.write('disp ')
		for strs in fdelist['disp']:
			file.write(strs+',')
		file.write('\n')
		for strs in fdelist['disp']:
			file.write('var')
			nodn = int(regx.search(r'[1-9]+',shap_tag1,regx.I).group())
			for nodi in range(nodn):
				file.write(' '+strs+str(nodi+1))
			file.write('\n')
	else:
		print('error: no disp declared')

	# write refc and coor declare
	if fdelist['coor'] != None:
		file.write('refc ')
		for strs in fdelist['coor']:
			file.write('r'+strs+',')
		file.write('\n')
		file.write('coor ')
		for strs in fdelist['coor']:
			file.write(strs+',')
		file.write('\n')
	else:
		print('error: no coor declared')

	# write func declare	
	if fdelist['func'] != None:
		file.write('func = ')
		for strs in fdelist['func']:
			file.write(strs+',')
		file.write('\n')

	# write dord declare
	if fdelist['disp'] != None:
		file.write('dord ')
		for strs in fdelist['disp']:
			file.write('1'+',')
		file.write('\n')
		
	file.write('node '+str(nodn)+'\n')
	
	# write code before mate declaration and tackle with 'singular' operator
	singular_list=[]
	if fdelist['code']['BFmate'] != None:
		release_BF_AF_mate_code(fdelist,'BFmate',file,pfelacpath,singular_list)
	
	# write mate line
	if fdelist['mate'] != None:
		file.write('mate')
		for strs in fdelist['mate']:
			file.write(' {}'.format(strs))
		file.write('\n')
	
	# write code after mate declaration and tackle with 'singular' operator	
	if fdelist['code']['AFmate'] != None:
		release_BF_AF_mate_code(fdelist,'AFmate',file,pfelacpath,singular_list)
	
	# write 'singular' operator declaration
	for line in singular_list:
		file.write(line)
		
	if fdelist['shap'] != None:
		pass
	
	file.close()