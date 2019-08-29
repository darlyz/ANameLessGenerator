'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the jason data to ges file
 All rights reserved
'''
import re as regx
import os

def xde2ges(gesname,coortype,keywd_tag,xde_lists,list_addr,keyws_reg,file):

	# 0 prepare
	shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
	gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
	if gaus_tag != None:
		gaus_tag = gaus_tag.group()
		
	dim = regx.search(r'[1-9]+',coortype,regx.I).group()
	axi = coortype.split('d')[1]
	
	
	file.write(gesname+'\ndefi\n')
	pfelacpath = os.environ['pfelacpath']
	
	code_use_dict = {} # use to deal with @L, @A, vol, singular, ...
	
	# 1 write disp and var declare
	# 1.1 parsing var
	var_dict = {}
	if 'disp' in xde_lists:
	
		for shap_type in xde_lists['shap'].keys():
		
			nodn = int(regx.search(r'[1-9]+',shap_type,regx.I).group())
			
			for var in xde_lists['shap'][shap_type]:
				var_dict[var] = []
				for ii in range(nodn):
					var_dict[var].append(var+str(ii+1))
				
	# 1.2 write disp declare
	if 'disp' in xde_lists:
		file.write('disp ')
		for strs in xde_lists['disp']:
			file.write(strs+',')
		file.write('\n')
		i = 0
		
	# 1.3 write var declare
	nodn = int(regx.search(r'[1-9]+',shap_tag,regx.I).group())
	if 'disp' in xde_lists:
		file.write('var')
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
		
	# 2 write refc and coor declare
	if 'coor' in xde_lists:
		file.write('refc ')
		for strs in xde_lists['coor']:
			file.write('r'+strs+',')
		file.write('\n')
		file.write('coor ')
		for strs in xde_lists['coor']:
			file.write(strs+',')
		file.write('\n')
	
	# 3 write func declare
	if 'func' in xde_lists:
		file.write('func = ')
		for strs in xde_lists['func']:
			file.write(strs+',')
		file.write('\n')

	# 4 write dord declare
	if 'disp' in xde_lists:
		file.write('dord ')
		for strs in xde_lists['disp']:
			file.write('1'+',')
		file.write('\n')
		
	# 5 write code before mate declaration and tackle with 'singular' operator
	#if 'BFmate' in xde_lists['code']:
		release_code(xde_lists,'BFmate',file,pfelacpath,code_use_dict)
	
	# 6 write mate line
	if 'mate' in xde_lists:
		file.write('mate')
		for var in xde_lists['mate']['default'].keys():
			file.write(' '+var)
		for var in xde_lists['mate']['default'].keys():
			file.write(' '+xde_lists['mate']['default'][var])
		file.write('\n')
		
	# 7 write code after mate declaration and tackle with 'singular' operator	
	#if xde_lists['code']['AFmate'] != None:
	#	release_code(xde_lists,list_addr,'AFmate',file,pfelacpath)
	
	# 8 write 'singular' operator declaration
	#if 'singular' in xde_lists:
	#	for line in xde_lists['singular']:
	#		file.write(line)
	
	# 9 write shap and tran paragraph
	file.write('\nshap\n')
	if 'shap' in xde_lists:
		geslib_coor = ['x','y','z']
		main_shap_string = ''
		
		# 9.1 write shap
		for shap_type in xde_lists['shap'].keys():
			
			shap_func = 'd'+dim+shap_type+'.sub'
			path_shap = pfelacpath+'ges\\ges.lib'
			file_shap = open(path_shap, mode='r')
			shap_find = 0
			shap_string = ''
			
			# 9.1.1 find shap function in ges.lib
			for line in file_shap.readlines():
				shap_start_file = regx.search('sub '+shap_func,line,regx.I)
				shap_end_file   = regx.search('end '+shap_func,line,regx.I)
				if shap_start_file != None:
					shap_find = 1
					continue
				if shap_end_file   != None:
					shap_find = 0
					continue
				if shap_find == 1:
					shap_string+=line
			file_shap.close()
			
			# note: save the main shap function for mix element when write tran
			if shap_type == shap_tag:
				main_shap_string = shap_string
			
			# 9.1.2 replace shap func's coor by xde's coor
			coor_i = 0
			for strs in xde_lists['coor']:
				shap_string = shap_string.replace(geslib_coor[coor_i],'r'+strs)
				coor_i += 1
			
			# 9.1.3 replace shap func's disp by xde's disp and write
			for strs in xde_lists['shap'][shap_type]:
				shap_string = shap_string.replace('u',strs)
				
				file.write(strs+'=\n')
				file.write(shap_string)
				file.write('\n')
		
		# 9.2 write tran
		file.write('tran\n')
		trans_list = main_shap_string.split('\n')
		trans_list.remove('')
		tran_list = []
		
		# 9.2.1 add '()'
		for strs in trans_list:
			temp_list = strs.split('=')
			temp_num = regx.search(r'[0-9]+',temp_list[0],regx.I).group()
			temp_list[0] = temp_list[0].replace(temp_num,'('+temp_num+')')
			tran_list.append(temp_list[0]+'='+temp_list[1])
		
		# 9.2.2 replace shap func's disp by by xde's coor and write
		shap_i = 0
		for strs in xde_lists['coor']:
			file.write(strs+'=\n')
			for strss in tran_list:
				file.write(strss.replace('u',strs)+'\n')
			file.write('\n')
			shap_i += 1
			
	# 9 write gaus paragraph
	if 'gaus' in xde_lists:

		# 9.1 Gaussian integral
		if xde_lists['gaus'][0] == 'g':
		
			gaus_degree = regx.search(r'[0-9]+',xde_lists['gaus'],regx.I).group()
		
			# 9.1.1 line square or cube shap
			if shap_tag[0].lower()=='l' \
			or shap_tag[0].lower()=='q' \
			or shap_tag[0].lower()=='c':
			
				path_gaus = pfelacpath+'ges\\gaus.pnt'
				file_gaus = open(path_gaus, mode='r')
				gaus_find = 0
				gaus_axis = []
				gaus_weit = []
				
				# 9.1.1.1 read gaus axis and weight in gaus.pnt
				for line in file_gaus.readlines():
					gaus_start_file = regx.search('n='+gaus_degree,line,regx.I)
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
				
				# 9.1.1.2 write line square or cube's gaussian integra
				file.write('gaus = '+str(len(gaus_weit)**int(dim))+'\n')
				
				if   shap_tag[0].lower()=='l':
					for axis_i in range(len(gaus_axis)):
						file.write(gaus_axis[axis_i]+' ' \
								  +gaus_weit[axis_i]+'\n')
						
				elif shap_tag[0].lower()=='q':
					for axis_i in range(len(gaus_axis)):
						for axis_j in range(len(gaus_axis)):
							weight = float(gaus_weit[axis_i]) \
									*float(gaus_weit[axis_j])
							file.write(gaus_axis[axis_i]+' ' \
									  +gaus_axis[axis_j]+' ' \
									  +str(weight)+'\n')
									  
				elif shap_tag[0].lower()=='c':
					for axis_i in range(len(gaus_axis)):
						for axis_j in range(len(gaus_axis)):
							for axis_k in range(len(gaus_axis)):
								weight = float(gaus_weit[axis_i]) \
										*float(gaus_weit[axis_j]) \
										*float(gaus_weit[axis_k])
								file.write(gaus_axis[axis_i]+' ' \
										  +gaus_axis[axis_j]+' ' \
										  +gaus_axis[axis_k]+' ' \
										  +str(weight)+'\n')
			
			# 9.1.2 triangle shap
			elif shap_tag[0].lower()=='t':
			
				path_gaus = pfelacpath+'ges\\gaust.pnt'
				file_gaus = open(path_gaus, mode='r')
				gaus_find = 0
				gaus_string = ''
				
				# 9.1.2.1 tackle the gaussian degree
				if gaus_degree == '6':
					gaus_degree = '5'
				elif int(gaus_degree) > 12 and int(gaus_degree) < 17:
					gaus_degree = '12'
				elif int(gaus_degree) > 17:
					gaus_degree = 17
				
				# 9.1.2.2 read gaus axis and weight in gaust.pnt and write
				for line in file_gaus.readlines():
					gaus_start_file = regx.search('P'+gaus_degree,line,regx.I)
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
			
			# 9.1.3  tetrahedron shap	
			elif shap_tag[0].lower()=='w':
			
				path_gaus = pfelacpath+'ges\\gausw.pnt'
				file_gaus = open(path_gaus, mode='r')
				gaus_find = 0
				gaus_string = ''
				
				# 9.1.3.1 tackle the gaussian degree
				if gaus_degree == '4':
					gaus_degree = '3'
				elif gaus_degree == '6':
					gaus_degree = '5'
				elif int(gaus_degree) > 7:
					gaus_degree = '7'
				
				# 9.1.2.2 read gaus axis and weight in gausw.pnt and write			
				for line in file_gaus.readlines():
					gaus_start_file = regx.search('P'+gaus_degree,line,regx.I)
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
				
			else: pass
		
		# 9.2 node integral	
		else:
			path_gaus = pfelacpath+'ges\\ges.lib'
			file_gaus = open(path_gaus, mode='r')
			gaus_find = 0
			gaus_string = ''
			
			# 9.2.1 read gaus axis and weight in ges.lib and write
			for line in file_gaus.readlines():
				gaus_start_file = regx.search('sub d'+dim+xde_lists['gaus']+'.gau',line,regx.I)
				gaus_end_file   = regx.search('end d'+dim+xde_lists['gaus']+'.gau',line,regx.I)
				if gaus_start_file != None:
					gaus_find = 1
					continue
				if gaus_end_file != None:
					gaus_find = 0
					continue
				if gaus_find == 1:
					gaus_string += line
					
			file_gaus.close()
			file.write(gaus_string)
		
	
	# 10 write func paragraph
	#if 'func' in xde_lists:
	#	if 'vol' in xde_lists:
	#		for line in xde_lists['vol']:
	#			file.write(line)
	#	if xde_lists['code']['func'] != None:
	#		release_code(xde_lists,list_addr,'func',file,pfelacpath)
	
	# 11 write stif paragraph
	#if 'stif' in xde_lists:
	#	file.write('\nstif\n')
	#	release_code(xde_lists,list_addr,'stif',file,pfelacpath)
	#	pass
	#else:
	#	print('error: no stif declared')
		
	# 12 write mass paragraph
	#file.write('\nmass\n')
	#if 'mass' in xde_lists:
	#	release_code(xde_lists,list_addr,'mass',file,pfelacpath)
	#	pass
		
	# 13 write damp paragraph
	#file.write('\ndamp\n')
	#if 'damp' in xde_lists:
	#	release_code(xde_lists,list_addr,'damp',file,pfelacpath)
	#	pass
		
	# 14 write load paragraph
	#file.write('\nload\n')
	#if 'load' in xde_lists:
	#	pass
	#else:
	#	print('error: no load declared')



def release_code(xde_lists,code_place,file,pfelacpath,code_use_dict):
	from expr import idx_summation
	from expr import idx_summation_lua
	from expr import complex_expr_trans

	for strs in xde_lists['code'][code_place]:
	
		regxrp = regx.search(r'Insr|Tnsr|Cplx|Oprt|Func',strs,regx.I)
		
		if   regxrp.group() == 'Insr':
			file.write(strs.replace('Insr_C:','$cc')+'\n')
		
		elif regxrp.group() == 'Tnsr':
		
			vector_expr = strs.replace('Tnsr_Asgn: ','')
			left_var  = vector_expr.split('=')[0].strip()
			righ_expr = vector_expr.split('=')[1].strip()

			expr_strs = idx_summation_lua(left_var,righ_expr,xde_lists)
			expr_list = expr_strs.rstrip('\n').split('\n')
			for strs in expr_list:
				file.write('$cc '+strs+';\n')

		elif regxrp.group() == 'Cplx':
			if strs.find('_') != -1:
				vector_expr = strs.replace('Cplx_Asgn: ','')
				left_var  = vector_expr.split('=')[0].strip()
				righ_expr = vector_expr.split('=')[1].strip()

				expr_strs = idx_summation_lua(left_var,righ_expr,xde_lists)
				expr_list = expr_strs.rstrip('\n').split('\n')

				for expr in expr_list:
					left_var  = expr.split('=')[0].strip()
					righ_expr = expr.split('=')[1].strip()

					cplx_list = complex_expr_trans(righ_expr)
					print(cplx_list)
					

	
	
	
		