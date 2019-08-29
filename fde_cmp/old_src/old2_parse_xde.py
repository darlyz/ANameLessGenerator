'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''
import re as regx

# key declare type1: DISP, COEF, COOR, GAUS, MATE
def pushkeydeclar (strs, linenum, line, keywd_tag, xde_lists, list_addr):
	if keywd_tag[strs] != 0:
		print('warn: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,keywd_tag[strs]))
	else:
		list_addr[strs] = linenum
		keywd_tag[strs] = linenum
		xde_lists[strs] = []
		wordlist = line.strip().split()
		for j in range(2,len(wordlist)+1): xde_lists[strs].append(wordlist[j-1])
		
# common declare type: VECT, FMATR	
def pushcomdeclar (strs, linenum, line, keywd_tag, xde_lists, list_addr):
	if keywd_tag[strs] == 0: 
		xde_lists[strs] = {}
		list_addr[strs] = {}
		keywd_tag[strs] = 1
	wordlist = line.strip().split()
	for j in range(2,len(wordlist)+1):
		if j == 2:
			xde_lists[strs][wordlist[1]]=[]
			list_addr[strs][wordlist[1]]=linenum
		else:
			xde_lists[strs][wordlist[1]].append(wordlist[j-1])
			
# common code line : @x, $Cx
def pushcommline (linenum, line, keywd_tag, xde_lists, list_addr):
	if   keywd_tag['paragraph'] == 'BFmate':
		xde_lists['code']['BFmate'].append(line.strip())
		list_addr['code']['BFmate'].append(linenum)
	elif keywd_tag['paragraph'] == 'AFmate':
		xde_lists['code']['AFmate'].append(line.strip())
		list_addr['code']['AFmate'].append(linenum)
	elif keywd_tag['paragraph'] == 'func':
		xde_lists['code']['func'].append(line.strip())
		list_addr['code']['func'].append(linenum)
	elif keywd_tag['paragraph'] == 'stif':
		xde_lists['code']['stif'].append(line.strip())
		list_addr['code']['stif'].append(linenum)
	elif keywd_tag['paragraph'] == 'mass':
		xde_lists['code']['mass'].append(line.strip())
		list_addr['code']['mass'].append(linenum)
	elif keywd_tag['paragraph'] == 'damp':
		xde_lists['code']['damp'].append(line.strip())
		list_addr['code']['damp'].append(linenum)
	else:
		print('error: line {}, wrong position inserted'.format(linenum))
		
# stif, mass, damp declare
def pushwekdeclar (strs, linenum, line, keywd_tag, xde_lists, list_addr):
	if keywd_tag[strs] != 0:
		print('error: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,keywd_tag[strs]))
		#break
	else:
		keywd_tag[strs] = linenum
		list_addr[strs] = linenum
		xde_lists[strs] = []
		wordlist = line.strip().split()
		if len(wordlist) != 1:
			for j in range(2,len(wordlist)+1):
				xde_lists[strs].append(wordlist[j-1])
		else:
			keywd_tag[strs+'type'] = 1
			keywd_tag['paragraph'] = strs

# complex 
def trans2complex (strs, xde_lists):
	temp_var = []
	for var in xde_lists[strs]:
		temp_var.append(var)
	xde_lists[strs] = []
	for var in temp_var:
		xde_lists[strs].append(var+'r')
		xde_lists[strs].append(var+'i')

def parse_xde(fdename, gesname, coortype, keywd_tag, xde_lists, list_addr, keyws_reg):

	#gesname
	shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
	gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
	if gaus_tag != None:
		gaus_tag = gaus_tag.group()
		
	dim = regx.search(r'[1-9]+',coortype,regx.I).group()
	axi = coortype.split('d')[1]
	
	file = open(fdename+'.fde', mode='r')
	#list = []
	#for line in file.readlines():
	#	line = line.strip(' ')
	#	list.append(line)
	#file.close()
	
	#for ll in list:
	#	print(ll)
	
	i = 0
	stitchline = ''
	keywd_tag['paragraph'] = 'BFmate'
	for line in file.readlines():
		i += 1
		
		# identify comment and stitch the next line begin with '\'
		line = stitchline+line
		if line.find('\\') != -1 :
			stitchline = line.split('\\')[0]
			continue
		else:
			stitchline = ''
			
		# skip comment line and blank line
		if line[0] == '\\' or line[0] == '\n':
			continue
		
		# identify commentbegin with '//'
		if line.find('//') != -1:
			line = line.split('//')[0]+'\n'
		
		#print(line)
		
		# retrieve the keywords
		regxrp = regx.search(keyws_reg,line,regx.I)
		if regxrp == None:
			if line.find('|') != -1:
				keywd_tag['complex'] = 1
		
			if line.find('[')!= -1 and line.find(']')!= -1:
				if   keywd_tag['paragraph'] == 'mass':
					xde_lists['mass'].append(line.strip())
				elif keywd_tag['paragraph'] == 'damp':
					xde_lists['damp'].append(line.strip())
				elif keywd_tag['paragraph'] == 'stif':
					xde_lists['stif'].append(line.strip())
				elif keywd_tag['paragraph'] == 'load':
					xde_lists['load'].append(line.strip())
				elif keywd_tag['paragraph'] == 'func':
					xde_lists['code']['func'].append(line.strip())
					list_addr['code']['func'].append(i)
			elif keywd_tag['matrixtag'] != 0 :
				if line.find('[')!= -1 or line.find(']')!= -1 :
					print('error: line {}, weak item is not allow to be contained in a matrix'.format(i))
				else:
					xde_lists['matrix'][keywd_tag['matrixname']].append(line.strip())
			else:
				print('redundant information or wrong declare, line {}: '.format(i)+line)
		elif regxrp.span()[0] != 0:
			keywd_tag['matrixtag'] = 0
			print('error: line {0}, keyword {1} must be at the head of line.'.format(i,regxrp.group()))
			#break
		else:
			keywd_tag['matrixtag'] = 0
			if   regxrp.group().lower() == 'disp':
				pushkeydeclar('disp', i, line, keywd_tag, xde_lists, list_addr)

			elif regxrp.group().lower() == 'coef':
				pushkeydeclar('coef', i, line, keywd_tag, xde_lists, list_addr)
	
			elif regxrp.group().lower() == 'coor':
				pushkeydeclar('coor', i, line, keywd_tag, xde_lists, list_addr)
				
			elif regxrp.group().lower() == 'gaus':
				pushkeydeclar('gaus', i, line, keywd_tag, xde_lists, list_addr)
	
			elif regxrp.group().lower() == 'mate':
				pushkeydeclar('mate', i, line, keywd_tag, xde_lists, list_addr)
				keywd_tag['paragraph'] = 'AFmate'
				
			elif regxrp.group().lower() == 'vect':
				if line.find('|') != -1:
					keywd_tag['complex'] = 1
				pushcomdeclar('vect', i, line, keywd_tag, xde_lists, list_addr)

			elif regxrp.group().lower() == 'fmatr':
				pushcomdeclar('fmatr',i, line, keywd_tag, xde_lists, list_addr)
				
			elif regxrp.group().lower() == 'fvect':
				pushcomdeclar('fvect',i, line, keywd_tag, xde_lists, list_addr)

			elif regxrp.group().find('$')!= -1 or regxrp.group().find('@')!= -1:
				if regxrp.group().lower() == '$cp':
					keywd_tag['complex'] = 1
				pushcommline (i, line, keywd_tag, xde_lists, list_addr)
				
			elif regxrp.group().lower() == 'mass':
				pushwekdeclar('mass', i, line, keywd_tag, xde_lists, list_addr)

			elif regxrp.group().lower() == 'damp':
				pushwekdeclar('damp', i, line, keywd_tag, xde_lists, list_addr)

			elif regxrp.group().lower() == 'stif':
				pushwekdeclar('stif', i, line, keywd_tag, xde_lists, list_addr)
				
			elif regxrp.group().lower() == 'shap':
				if keywd_tag['shap'] == 0:
					list_addr['shap'] = []
					xde_lists['shap'] = []
					keywd_tag['shap'] = 1
				list_addr['shap'].append(i)
				wordlist = line.strip().split()
				wordlist.pop(0)
				xde_lists['shap'].append(wordlist)
	
			elif regxrp.group().lower() == 'dist':
				if keywd_tag['paragraph'] == 'mass':
					xde_lists['mass'].append('dist')
					xde_lists['mass'].append(line.split('=')[1].strip())
				elif keywd_tag['paragraph'] == 'damp':
					xde_lists['damp'].append('dist')
					xde_lists['damp'].append(line.split('=')[1].strip())
				elif keywd_tag['paragraph'] == 'stif':
					xde_lists['stif'].append('dist')
					xde_lists['stif'].append(line.split('=')[1].strip())
					
			elif regxrp.group().lower() == 'load':
				if keywd_tag['load'] == 0:
					xde_lists['load'] = []
				xde_lists['load'].append(line.split('=')[1].strip())
				keywd_tag['paragraph'] = 'load'
			
			elif regxrp.group().lower() == 'func':
				wordlist = line.strip().split()
				if len(wordlist) != 1:
					if keywd_tag['func'] == 0:
						xde_lists['func'] = []
					keywd_tag['func'] = 1
					for j in range(2,len(wordlist)+1): xde_lists['func'].append(wordlist[j-1])
				else:
					keywd_tag['paragraph'] = 'func'
					
			elif regxrp.group().lower() == 'matrix':
				pushcomdeclar('matrix', i, line, keywd_tag, xde_lists, list_addr)
				wordlist = line.strip().split()
				keywd_tag['matrixname'] = wordlist[1]
				keywd_tag['matrixtag'] = 1
	
			elif regxrp.group().lower() == 'end':
				print('reading end')

			else: print(str(line))

	file.close()
	
	# checking
	#check_xde(xde_lists)

	nodn = regx.search(r'[1-9]+',shap_tag,regx.I).group()
	shap_type = shap_tag[0]

	# pasing shap of disp and coef
	if keywd_tag['complex'] == 1:
		if 'disp' in xde_lists:
			trans2complex ('disp', xde_lists)
		if 'coef' in xde_lists:
			trans2complex ('coef', xde_lists)
		if 'func' in xde_lists:
			trans2complex ('func', xde_lists)
	
	shap_dict = {}
	shap_list = xde_lists['shap'].copy()
	if xde_lists['shap'] != None:
		shap_i = 0
		for shp_list in shap_list:
			if len(shp_list) == 2:
				if (shp_list[0][0] == '%' and shp_list[0][1] != '1') or (shp_list[1][0] == '%' and shp_list[1][1] != '2'):
					print('error: line {}, suggested format is \'SHAP %1 %2\''.format(list_addr['shap'][shap_i]))
				else:
					if  shp_list[0] == '%1':
						shp_list[0] = shap_type
					if  shp_list[1] == '%2':
						shp_list[1] = nodn
					shap_dict[shp_list[0]+shp_list[1]] = []
					for disp_var in xde_lists['disp']:
						shap_dict[shp_list[0]+shp_list[1]].append(disp_var)
				if 'coef' in xde_lists:
					xde_lists['coef_shap'] = {}
					xde_lists['coef_shap'][shp_list[0]+shp_list[1]] = []
					for coef_var in xde_lists['coef']:
						xde_lists['coef_shap'][shp_list[0]+shp_list[1]].append(coef_var)
			shap_i += 1

		shap_i = 0
		for shp_list in shap_list:
			if len(shp_list) >= 3:
				if shp_list[0] == '%1':
					shp_list[0] = shap_type
				
				if shp_list[1] == '%4':
					disp_find_n = xde_lists['disp'].count(shp_list[2])
					coef_find_n = 0
					if 'coef' in xde_lists:
						coef_find_n = xde_lists['coef'].count(shp_list[2])
					var_name = shp_list[2]
					if disp_find_n == 1 and coef_find_n == 0:
						shap_dict[shp_list[2]] = []
						if   shap_tag == 't6':  shp_list[1] = '3'
						elif shap_tag == 'q9':  shp_list[1] = '4'
						elif shap_tag == 'w10': shp_list[1] = '4'
						elif shap_tag == 'c27': shp_list[1] = '8'
						else:
							print('error: line {}, mix element should to be used in 2nd shap function'.format(list_addr['shap'][shap_i]))
						shp_list.pop(2)
						shap_dict[var_name] = shp_list
					elif disp_find_n == 0 and coef_find_n == 1:
						xde_lists['coef_shap'][shp_list[2]] = []
						if   shap_tag == 't6':  shp_list[1] = '3'
						elif shap_tag == 'q9':  shp_list[1] = '4'
						elif shap_tag == 'w10': shp_list[1] = '4'
						elif shap_tag == 'c27': shp_list[1] = '8'
						else:
							print('error: line {}, mix element should to be used in 2nd shap function'.format(list_addr['shap'][shap_i]))
						shp_list.pop(2)
						xde_lists['coef_shap'][var_name] = shp_list
					else:
						print('error: line {}, disp or coef declaration fault.'.format(list_addr['shap'][shap_i]))
				elif shp_list[1] == '%2c':
					shp_list[1] = shp_list[1].replace('%2',nodn)
					pena_var = shp_list[2].split('_')[0]
					be_penal = shp_list[2].split('_')[1]
					print(pena_var,be_penal)
					if xde_lists['disp'].count(pena_var) == 1 and xde_lists['disp'].count(be_penal) == 1:
						shp_list[2] = be_penal
						shap_dict[pena_var] = shp_list
			shap_i += 1
	xde_lists['shap'] = shap_dict
	
	# pasing gaus
	if gaus_tag != None:
		xde_lists['gaus'] = gaus_tag
	else:
		xde_lists['gaus'] = shap_tag
		
	# parsing mass and damp
	if 'mass' in xde_lists:
		if xde_lists['mass'][0] == '%1':
			xde_lists['mass'][0] = 'lump'
	if 'damp' in xde_lists:
		if xde_lists['damp'][0] == '%1':
			xde_lists['damp'][0] = 'lump'
		
	
	