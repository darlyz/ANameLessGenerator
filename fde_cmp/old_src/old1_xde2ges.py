'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the jason data to ges file
 All rights reserved
'''
import re as regx
import os

def xde2ges(gesname,keywdtag,xde_lists,listaddrs,regkeyws,coortype):

	#gesname = 'aec8g2'
	shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
	gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
	if gaus_tag != None:
		gaus_tag = gaus_tag.group()
		
	dim = regx.search(r'[1-9]+',coortype,regx.I).group()
	axi = coortype.split('d')[1]
	
	file = open(gesname+'.ges1', mode='w')
	file.write(gesname+'\ndefi\n')
	
	pfelacpath = os.environ['pfelacpath']

	# pasing var
	var_dict = {}
	nodn = int(regx.search(r'[1-9]+',shap_tag,regx.I).group())
	shap_i = 0
	for shp_list in xde_lists['shap']:
		if len(shp_list) == 2:
			if (shp_list[0][0] == '%' and shp_list[0][1] != '1') or (shp_list[1][0] == '%' and shp_list[1][1] != '2'):
				print('error: line {}, suggested format is \'SHAP %1 %2\''.format(listaddrs['shap'][shap_i]))
			
			for disp_var in xde_lists['disp']:
				for nodi in range(nodn):
					if nodi == 0:
						var_dict[disp_var] = []
					var_dict[disp_var].append(disp_var+str(nodi+1))
		elif len(shp_list) == 3:
			if shp_list[1] == '%4':
				if xde_lists['disp'].count(shp_list[2]) == 1:
					var_dict[shp_list[2]] = []
					if shap_tag == 't6':
						for nodi in range(3):
							var_dict[shp_list[2]].append(shp_list[2]+str(nodi+1))
					elif shap_tag == 'q9' or shap_tag == 'w10':
						for nodi in range(4):
							var_dict[shp_list[2]].append(shp_list[2]+str(nodi+1))
					elif shap_tag == 'c27':
						for nodi in range(8):
							var_dict[shp_list[2]].append(shp_list[2]+str(nodi+1))
					else:
						print('error: mix element should to be used in 2nd shap function')
				elif xde_lists['disp'].count(shp_list[2]) == 0:
					print('error: line {}, disp var \'{}\' should be found in disp declaration line {}.'.format(listaddrs['shap'][shap_i],shp_list[2],listaddrs['disp']))
				else:
					print('error: line {}, duplicated disp declaration \'{}\'.'.format(listaddrs['disp'],shp_list[2]))
			elif shp_list[1] == '%4c':pass
			elif shp_list[1] == '%2c':pass
			else: pass
		else: pass
		shap_i += 1
		
	print(var_dict)
	# write disp and var declare
	if xde_lists['disp'] != None:
		file.write('disp ')
		for strs in xde_lists['disp']:
			file.write(strs+',')
		file.write('\n')
		i = 0
		
		file.write('var')
		#for nodi in range(nodn):
		#	for strs in xde_lists['disp']:
		#		file.write(' '+var_dict[strs][nodi])
		#		i += 1
		#		if i == 10:
		#			file.write('\nvar')
		#			i = 0
					
		for nodi in range(nodn):
			for strs in xde_lists['disp']:
				if nodi >= len(var_dict[strs]):
					continue
				file.write(' '+var_dict[strs][nodi])
				i += 1
				if i == 10:
					file.write('\nvar')
					i = 0
			
		file.write('\n')
	else:
		print('error: no disp declared')

	# write refc and coor declare
	if xde_lists['coor'] != None:
		file.write('refc ')
		for strs in xde_lists['coor']:
			file.write('r'+strs+',')
		file.write('\n')
		file.write('coor ')
		for strs in xde_lists['coor']:
			file.write(strs+',')
		file.write('\n')
	else:
		print('error: no coor declared')

	# write func declare	
	if xde_lists['func'] != None:
		file.write('func = ')
		for strs in xde_lists['func']:
			file.write(strs+',')
		file.write('\n')

	# write dord declare
	if xde_lists['disp'] != None:
		file.write('dord ')
		for strs in xde_lists['disp']:
			file.write('1'+',')
		file.write('\n')
		
	file.write('node '+str(nodn)+'\n')
	
	# write code before mate declaration and tackle with 'singular' operator
	if xde_lists['code']['BFmate'] != None:
		release_code(xde_lists,listaddrs,'BFmate',file,pfelacpath)
	
	# write mate line
	if xde_lists['mate'] != None:
		file.write('mate')
		for strs in xde_lists['mate']:
			file.write(' {}'.format(strs))
		file.write('\n')
	
	# write code after mate declaration and tackle with 'singular' operator	
	if xde_lists['code']['AFmate'] != None:
		release_code(xde_lists,listaddrs,'AFmate',file,pfelacpath)
	
	# write 'singular' operator declaration
	if 'singular' in xde_lists:
		for line in xde_lists['singular']:
			file.write(line)
	
	# write shap and tran paragraph
	if xde_lists['shap'] != None:
		release_shap(xde_lists,listaddrs,file,pfelacpath,shap_tag,dim)
	else:
		print('error: no shap declared')

	# write gaus paragraph
	if xde_lists['gaus'] != None:
		release_gaus(file,pfelacpath,shap_tag,gaus_tag,dim)
	else:
		print('error: no gaus declared')
	
	# write func paragraph
	file.write('\nfunc\n')
	if 'vol' in xde_lists:
		for line in xde_lists['vol']:
			file.write(line)
	if xde_lists['code']['func'] != None:
		release_code(xde_lists,listaddrs,'func',file,pfelacpath)
		
	# write stif paragraph
	file.write('\nstif\n')
	if xde_lists['stif'] != None:
		release_code(xde_lists,listaddrs,'stif',file,pfelacpath)
		pass
	else:
		print('error: no stif declared')
		
	# write mass paragraph
	file.write('\nmass\n')
	if xde_lists['mass'] != None:
		release_code(xde_lists,listaddrs,'mass',file,pfelacpath)
		pass
		
	# write damp paragraph
	file.write('\ndamp\n')
	if xde_lists['damp'] != None:
		release_code(xde_lists,listaddrs,'damp',file,pfelacpath)
		pass
		
	# write load paragraph
	file.write('\nload\n')
	if xde_lists['damp'] != None:
		pass
	else:
		print('error: no load declared')
	
	file.close()
	
def release_code(xde_lists,listaddrs,code_place,file,pfelacpath):
	i = 0
	for strs in xde_lists['code'][code_place]:
		i += 1
		operator_list = []
		operator_strs = ''
		line_num = listaddrs['code'][code_place][i-1]
		regxrp = regx.search('\$CC|\$CP|\$CV|@L|@W|@A|@S|@R',strs,regx.I)
		
		if regxrp.group().lower() == '$cc': # <------- could add the function of checking mate variable
			file.write(strs+'\n')
		elif regxrp.group().lower() == '$cv': # <------- need to add function
			pass
		elif regxrp.group().lower() == '$cp': # <------- need to add function
			pass
		elif regxrp.group().lower() == '@l':
			opr_list = strs.split()
			operator_expr = ''
			operator_name = ''
			operator_coor = ''
			
			# checking
			operator_find = 0
			if len(opr_list) == 1:
				print('error: line {}, no operator name, reference format: @L [operator] [x] .., where x is one of \'n|c|v|m|f\'.'.format(line_num))
			else:
				operator_expr = opr_list[1]
				if operator_expr.find('.') == -1:
					print('error: line {}, {} is wrong operator format, reference: \'[name].[axis]\'.'.format(line_num,operator_expr))
				else:
					path_opr = pfelacpath+'ges\\pdesub'
					file_opr = open(path_opr, mode='r')
					for line in file_opr.readlines():
						if operator_expr.lower() == line.strip():
							operator_find = 1
					file_opr.close()
					if operator_find == 0:
						print('error: line {}, \'{}\' is not a defaut operator, make sure it\'s defined in \'{}\''.format(line_num,operator_expr,pfelacpath+'ges\\pde.lib'))
					else:
						operator_name = operator_expr.split('.')[0]
						operator_coor = operator_expr.split('.')[1]
						coor_true = ''
						for ww in xde_lists['coor']: coor_true += ww
						
						if operator_coor.lower() != coor_true.lower():
							print('warning: line {}, postfix of operator \'{}\' is \'{}\' but not \'{}\': \'{}\'?'.format(line_num,operator_name,operator_coor,coor_true,operator_expr))
						
						if operator_name.lower() == 'singular' or operator_name.lower() == 'vol':
							xde_lists[operator_name.lower()] = []
							if len(opr_list)==2:
								print('error: line {}, not enough parameter, reference format: @L {} n.'.format(line_num,operator_expr))
							elif opr_list[2].lower() != 'n':
								print('error: line {}, wrong parameter, reference format: @L {} n.'.format(line_num,operator_expr))
						elif regx.search(r'curl|grad|div|laplace',operator_name,regx.I) != None:
							if len(opr_list)==2:
								print('error: line {}, not enough parameter, reference format: @L {} [x] .., where x is one of \'c|v|m|f\'.'.format(line_num,operator_expr))
							elif regx.search(r'c|v|m|f',opr_list[2],regx.I) == None:
								print('error: line {}, reference format: @L {} [x] .., where x is one of \'c|v|m|f\'.'.format(line_num,operator_expr))
						elif operator_name.lower() == 'deform' or operator_name.lower() == 'isotropi':
							pass # <------------------ need to do	
						else:
							print('warning: line {}, \'{}\' is not a defaut operator, make sure it\'s defined in \'{}\''.format(line_num,operator_name,pfelacpath+'ges\\pde.lib'))
			
			# parsing
			operator_find = 0
			opr_var_list = []
			lib_var_list = []
			if len(opr_list)>2:
				path_opr = pfelacpath+'ges\\pde.lib'
				file_opr = open(path_opr, mode='r')
				if opr_list[2] == 'n': # singular vol
					if len(opr_list)>3:
						print('warning: line {}, redundant parameters, but ignore them.'.format(line_num))
					
					for line in file_opr.readlines():
						operator_start_file = regx.search('sub '+operator_expr,line,regx.I)
						operator_end_file   = regx.search('end '+operator_expr,line,regx.I)
						if operator_start_file != None:
							operator_find = 1
							continue
						if operator_end_file   != None:
							operator_find = 0
							continue
						if operator_find == 1:
							xde_lists[operator_name.lower()].append(line)
					
				elif opr_list[2] == 'c': # grad.x grad.r grad.s gradv.x div curl.xy curl.ro curl.rz curl.rs laplaces
					if len(opr_list) == 4:
						opr_var_list.extend(xde_lists['coor'])
						opr_var_list.extend(xde_lists['disp'])
					else:
						for ii in range(4,len(opr_list)):
							opr_var_list.append(opr_list[ii])
							
					for line in file_opr.readlines():
						operator_start_file = regx.search('sub '+operator_expr,line,regx.I)
						operator_end_file   = regx.search('end '+operator_expr,line,regx.I)
						if operator_start_file != None:
							operator_find = 1
							lib_var_strs = line.split('(')[1].rstrip().rstrip(')')
							lib_var_list = lib_var_strs.split(',')
							continue
						if operator_end_file   != None:
							operator_find = 0
							continue
						if operator_find == 1:
							operator_strs += line
					
					if len(opr_var_list) == len(lib_var_list):
						for ii in range(len(opr_var_list)):
							operator_strs = operator_strs.replace(lib_var_list[ii],opr_var_list[ii])
						operator_strs = operator_strs.replace('[','{')
						operator_strs = operator_strs.replace(']','}')
						file.write('$cc {}='.format(opr_list[3]))
						file.write(operator_strs)
					else:
						if len(opr_list) == 4:
							print('error: line {}, \'{}\'s defaut variable is made up by coor and disp:'.format(line_num,operator_expr))
							print('                \'{}\', are not match to \'{}\'.'.format(opr_var_list,lib_var_list))
						else:
							print('error: line {}, \'{}\'s variable \'{}\', are not match to \'{}\'.'.format(line_num,operator_expr,opr_var_list,lib_var_list))
					
				elif opr_list[2] == 'v': # else
					pass
				elif opr_list[2] == 'm': # gradv
					pass
				elif opr_list[2] == 'f':
					pass
				
				file_opr.close()
				
def release_gaus(file,pfelacpath,shap_tag,gaus_tag,dim):
	gaus_axis = []
	gaus_weit = []
	gaus_degr = regx.search(r'[0-9]+',gaus_tag,regx.I).group()
	if shap_tag[0].lower()=='l' or shap_tag[0].lower()=='q' or shap_tag[0].lower()=='c':
		# Gaussian integral
		if gaus_tag != None:
			path_gaus = pfelacpath+'ges\\gaus.pnt'
			file_gaus = open(path_gaus, mode='r')
			gaus_find = 0

			for line in file_gaus.readlines():
				gaus_start_file = regx.search('n='+gaus_degr,line,regx.I)
				if gaus_start_file != None:
					gaus_find = 1
					continue
				if gaus_find == 1 and line=='\n':
					gaus_find = 0
					continue
				if gaus_find == 1:
					gaus_string = line.split()
					if gaus_string[0][0] != '-':
						gaus_string[0] = ' '+gaus_string[0]
					gaus_axis.append(gaus_string[0])
					gaus_weit.append(gaus_string[1])

			file_gaus.close()
			file.write('gaus = '+str(len(gaus_weit)**int(dim))+'\n')
			if   shap_tag[0].lower()=='l':
				for axis_i in range(len(gaus_axis)):
					file.write(gaus_axis[axis_i]+' '+gaus_weit[axis_i]+'\n')
			elif shap_tag[0].lower()=='q':
				for axis_i in range(len(gaus_axis)):
					for axis_j in range(len(gaus_axis)):
						weight = float(gaus_weit[axis_i])*float(gaus_weit[axis_j])
						file.write(gaus_axis[axis_i]+' '+gaus_axis[axis_j]+' '+str(weight)+'\n')
			elif shap_tag[0].lower()=='c':
				for axis_i in range(len(gaus_axis)):
					for axis_j in range(len(gaus_axis)):
						for axis_k in range(len(gaus_axis)):
							weight = float(gaus_weit[axis_i])*float(gaus_weit[axis_j])*float(gaus_weit[axis_k])
							file.write(gaus_axis[axis_i]+' '+gaus_axis[axis_j]+' '+gaus_axis[axis_k]+' '+str(weight)+'\n')
		# nodal integration
		else:
			if   shap_tag == 'l2':
				file.write('gaus = 2\n'+'-1. 1.\n'+' 1. 1.\n')
			elif shap_tag == 'l3':
				file.write('gaus = 3\n'+'-1. 1./3.\n'+' 0. 4./3.\n'+' 1. 1./3.\n')
			elif shap_tag == 'q4':
				file.write('gaus = 4\n')
				file.write('-1. -1. 1.\n')
				file.write(' 1. -1. 1.\n')
				file.write(' 1.  1. 1.\n')
				file.write('-1.  1. 1.\n')
			elif shap_tag == 'q9':
				file.write('gaus = 9\n')
				file.write('-1. -1.  1./9.\n')
				file.write(' 1. -1.  1./9.\n')
				file.write(' 1.  1.  1./9.\n')
				file.write('-1.  1.  1./9.\n')
				file.write(' 0. -1.  4./9.\n')
				file.write(' 1.  0.  4./9.\n')
				file.write(' 0.  1.  4./9.\n')
				file.write('-1.  0.  4./9.\n')
				file.write(' 0.  0. 16./9.\n')
			elif shap_tag == 'c8':
				file.write('gaus = 8\n')
				file.write('-1. -1. -1.  1.\n')
				file.write(' 1. -1. -1.  1.\n')
				file.write(' 1.  1. -1.  1.\n')
				file.write('-1.  1. -1.  1.\n')
				file.write('-1. -1.  1.  1.\n')
				file.write(' 1. -1.  1.  1.\n')
				file.write(' 1.  1.  1.  1.\n')
				file.write('-1.  1.  1.  1.\n')
			elif shap_tag == 'c27':
				file.write('gaus = 27\n')
				file.write('-1. -1. -1.   1./27.\n')
				file.write(' 1. -1. -1.   1./27.\n')
				file.write(' 1.  1. -1.   1./27.\n')
				file.write('-1.  1. -1.   1./27.\n')
				file.write('-1. -1.  1.   1./27.\n')
				file.write(' 1. -1.  1.   1./27.\n')
				file.write(' 1.  1.  1.   1./27.\n')
				file.write('-1.  1.  1.   1./27.\n')
				file.write(' 0. -1. -1.   4./27.\n')
				file.write(' 1.  0. -1.   4./27.\n')
				file.write(' 0.  1. -1.   4./27.\n')
				file.write('-1.  0. -1.   4./27.\n')
				file.write('-1. -1.  0.   4./27.\n')
				file.write(' 1. -1.  0.   4./27.\n')
				file.write(' 1.  1.  0.   4./27.\n')
				file.write('-1.  1.  0.   4./27.\n')
				file.write(' 0. -1.  1.   4./27.\n')
				file.write(' 1.  0.  1.   4./27.\n')
				file.write(' 0.  1.  1.   4./27.\n')
				file.write('-1.  0.  1.   4./27.\n')
				file.write(' 0.  0. -1.  16./27.\n')
				file.write(' 0. -1.  0.  16./27.\n')
				file.write(' 1.  0.  0.  16./27.\n')
				file.write(' 0.  1.  0.  16./27.\n')
				file.write('-1.  0.  0.  16./27.\n')
				file.write(' 0.  0.  1.  16./27.\n')
				file.write(' 0.  0.  0.  64./27.\n')
			else: pass # need to extend

	elif shap_tag[0].lower()=='t':
		# Gaussian integral
		if gaus_tag != None:
			path_gaus = pfelacpath+'ges\\gaust.pnt'
			file_gaus = open(path_gaus, mode='r')
			gaus_find = 0
			gaus_string = ''
			if gaus_degr == '6':
				gaus_degr = '5'
			elif int(gaus_degr) > 12 and int(gaus_degr) < 17:
				gaus_degr = '12'
			elif int(gaus_degr) > 17:
				gaus_degr = 17
			
			for line in file_gaus.readlines():
				gaus_start_file = regx.search('P'+gaus_degr,line,regx.I)
				if gaus_start_file != None:
					gaus_find = 1
					continue
				if gaus_find == 1 and line=='\n':
					gaus_find = 0
					continue
				if gaus_find == 1:
					gaus_string += line

			file_gaus.close()
			file.write(gaus_string)
		# nodal integration
		else:
			if   shap_tag == 't3':
				file.write('gaus =  3\n')
				file.write('1.  0.  1./6.\n')
				file.write('0.  1.  1./6.\n')
				file.write('0.  0.  1./6.\n')
			elif shap_tag == 't6':
				file.write('gaus =  6\n')
				file.write('1.  0.  0.125/3.\n')
				file.write('0.5 0.5 0.125\n')
				file.write('0.  1.  0.125/3.\n')
				file.write('0.  0.5 0.125\n')
				file.write('0.  0.  0.125/3.\n')
				file.write('0.5 0.  0.125\n')
			else: pass # need to extend
				
	elif shap_tag[0].lower()=='w':
		# Gaussian integral
		if gaus_tag != None:
			path_gaus = pfelacpath+'ges\\gausw.pnt'
			file_gaus = open(path_gaus, mode='r')
			gaus_find = 0
			gaus_string = ''
			if gaus_degr == '4':
				gaus_degr = '3'
			elif gaus_degr == '6':
				gaus_degr = '5'
			elif int(gaus_degr) > 7:
				gaus_degr = '7'
			
			for line in file_gaus.readlines():
				gaus_start_file = regx.search('P'+gaus_degr,line,regx.I)
				if gaus_start_file != None:
					gaus_find = 1
					continue
				if gaus_find == 1 and line=='\n':
					gaus_find = 0
					continue
				if gaus_find == 1:
					gaus_string += line

			file_gaus.close()
			file.write(gaus_string)
		# nodal integration
		else:
			if   shap_tag == 'w4':
				file.write('gaus = 4\n')
				file.write('1. 0. 0. 1./24.\n')
				file.write('0. 1. 0. 1./24.\n')
				file.write('0. 0. 0. 1./24.\n')
				file.write('0. 0. 1. 1./24.\n')
			elif shap_tag == 'w10':
				file.write('gaus = 10\n')
				file.write('1. 0. 0. 1./96.\n')
				file.write('.5 .5 0. 1./48.\n')
				file.write('0. 1. 0. 1./96.\n')
				file.write('0. .5 .5 1./48.\n')
				file.write('0. 0. 1. 1./96.\n')
				file.write('.5 0. .5 1./48.\n')
				file.write('.5 0. 0. 1./48.\n')
				file.write('0. .5 0. 1./48.\n')
				file.write('0. 0. .5 1./48.\n')
				file.write('0. 0. 0. 1./96.\n')
			else: pass # need to extend

	else: pass # need to extend				

def release_shap(xde_lists,listaddrs,file,pfelacpath,shap_tag,dim):
	shap_string1=''
	shap_string2=''
	shap_list = []
	lib_coor_list = ['x','y','z']
	shap_i = 0

	# parse
	for shaplist in xde_lists['shap']:
		if len(shaplist) == 2:
			if shaplist[0] == '%1': shaplist[0] = regx.search(r'[ltqwc]',shap_tag,regx.I).group()
			if shaplist[1] == '%2': shaplist[1] = regx.search(r'[1-9]+', shap_tag,regx.I).group()
			
			path_shap = pfelacpath+'ges\\ges.lib'
			file_shap = open(path_shap, mode='r')
			shap_name = 'd'+dim+shaplist[0]+shaplist[1]
			shap_find = 0
			
			for line in file_shap.readlines():
				shap_start_file = regx.search('sub '+shap_name+'.sub',line,regx.I)
				shap_end_file   = regx.search('end '+shap_name+'.sub',line,regx.I)
				if shap_start_file != None:
					shap_find = 1
					continue
				if shap_end_file   != None:
					shap_find = 0
					continue
				if shap_find == 1:
					shap_string1+=line
			file_shap.close()
			
			coor_i = 0
			for strs in xde_lists['coor']:
				shap_string1 = shap_string1.replace(lib_coor_list[coor_i],'r'+strs)
				coor_i += 1
			
			for strs in xde_lists['disp']:
				temp_string = shap_string1.replace('u',strs)
				shap_list.append(temp_string)
		elif len(shaplist) > 2: # <------------------ need to do
			pass
		else:
			print('error: line {}, not enough shap declaration'.format(listaddrs['shap'][shap_i]))

		shap_i += 1

	# write
	file.write('\nshap\n')
	shap_i = 0
	for shaplist in shap_list:
		file.write(xde_lists['disp'][shap_i]+'=\n')
		file.write(shaplist)
		file.write('\n')
		shap_i += 1
		
	file.write('tran\n')
	trans_list = shap_string1.split('\n')
	trans_list.remove('')
	tran_list = []
	for strs in trans_list:
		temp_list = strs.split('=')
		temp_num = regx.search(r'[0-9]+',temp_list[0],regx.I).group()
		temp_list[0] = temp_list[0].replace(temp_num,'('+temp_num+')')
		tran_list.append(temp_list[0]+'='+temp_list[1])
	
	shap_i = 0
	for strs in xde_lists['coor']:
		file.write(strs+'=\n')
		for strss in tran_list:
			file.write(strss.replace('u',strs)+'\n')
		file.write('\n')
		shap_i += 1


