'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''
import re as regx

# key declare type1: DISP, COOR, GAUS, MATE
def pushkeydeclar (strs, linenum, line, keywdtag, xde_lists, listaddrs):
	if keywdtag[strs] != 0:
		print('warn: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,keywdtag[strs]))
	else:
		listaddrs[strs] = linenum
		xde_lists[strs] = []
		wordlist = line.strip().split()
		for j in range(2,len(wordlist)+1): xde_lists[strs].append(wordlist[j-1])
		
# common declare type: VECT, FMATR	
def pushcomdeclar (strs, linenum, line, keywdtag, xde_lists, listaddrs):
	if keywdtag[strs] == 0: 
		xde_lists[strs] = {}
		listaddrs[strs] = {}
		keywdtag[strs] = 1
	wordlist = line.strip().split()
	for j in range(2,len(wordlist)+1):
		if j == 2:
			xde_lists[strs][wordlist[1]]=[]
			listaddrs[strs][wordlist[1]]=linenum
		else:
			xde_lists[strs][wordlist[1]].append(wordlist[j-1])
			
# common code line : @x, $Cx
def pushcommline (linenum, line, keywdtag, xde_lists, listaddrs):
	if   keywdtag['paragraph'] == 'BFmate':
		xde_lists['code']['BFmate'].append(line.strip())
		listaddrs['code']['BFmate'].append(linenum)
	elif keywdtag['paragraph'] == 'AFmate':
		xde_lists['code']['AFmate'].append(line.strip())
		listaddrs['code']['AFmate'].append(linenum)
	elif keywdtag['paragraph'] == 'func':
		xde_lists['code']['func'].append(line.strip())
		listaddrs['code']['func'].append(linenum)
	elif keywdtag['paragraph'] == 'stif':
		xde_lists['code']['stif'].append(line.strip())
		listaddrs['code']['stif'].append(linenum)
	elif keywdtag['paragraph'] == 'mass':
		xde_lists['code']['mass'].append(line.strip())
		listaddrs['code']['mass'].append(linenum)
	elif keywdtag['paragraph'] == 'damp':
		xde_lists['code']['damp'].append(line.strip())
		listaddrs['code']['damp'].append(linenum)
	else:
		print('error: line {}, wrong position inserted'.format(linenum))
		
# stif, mass, damp declare
def pushwekdeclar (strs, linenum, line, keywdtag, xde_lists, listaddrs):
	if keywdtag[strs] != 0:
		print('error: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,keywdtag[strs]))
		#break
	else:
		keywdtag[strs] = linenum
		listaddrs[strs] = linenum
		xde_lists[strs] = []
		wordlist = line.strip().split()
		if len(wordlist) != 1:
			for j in range(2,len(wordlist)+1):
				xde_lists[strs].append(wordlist[j-1])
		else:
			keywdtag[strs+'type'] = 1
			keywdtag['paragraph'] = strs

def parse_xde(fdename,keywdtag,xde_lists,listaddrs,regkeyws,coortype):

	dim = int(regx.search(r'[1-9]+',coortype,regx.I).group())
	axi = coortype.split('d')[1]
	
	list = []
	file = open(fdename+'.fde', mode='r')
	for line in file.readlines():
		line = line.strip(' ')
		list.append(line)
	file.close()
	
	#for ll in list:
	#	print(ll)
	
	i = 0
	stitchline = ''
	keywdtag['paragraph'] = 'BFmate'
	for line in list:
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
		regxrp = regx.search(regkeyws,line,regx.I)
		if regxrp == None:
			if line.find('[')!= -1 and line.find(']')!= -1:
				if   keywdtag['paragraph'] == 'mass':
					xde_lists['mass'].append(line.strip())
				elif keywdtag['paragraph'] == 'damp':
					xde_lists['damp'].append(line.strip())
				elif keywdtag['paragraph'] == 'stif':
					xde_lists['stif'].append(line.strip())
				elif keywdtag['paragraph'] == 'load':
					xde_lists['load'].append(line.strip())
				elif keywdtag['paragraph'] == 'func':
					xde_lists['code']['func'].append(line.strip())
					listaddrs['code']['func'].append(i)
			elif keywdtag['matrixtag'] != 0 :
				if line.find('[')!= -1 or line.find(']')!= -1 :
					print('error: line {}, weak item is not allow to be contained in a matrix'.format(i))
				else:
					xde_lists['matrix'][keywdtag['matrixname']].append(line.strip())
			else:
				print('redundant information or wrong declare, line {}: '.format(i)+line)
		elif regxrp.span()[0] != 0:
			keywdtag['matrixtag'] = 0
			print('error: line {0}, keyword {1} must be at the head of line.'.format(i,regxrp.group()))
			#break
		else:
			keywdtag['matrixtag'] = 0
			if   regxrp.group().lower() == 'disp':
				pushkeydeclar('disp', i, line, keywdtag, xde_lists, listaddrs)
	
			elif regxrp.group().lower() == 'coor':
				pushkeydeclar('coor', i, line, keywdtag, xde_lists, listaddrs)
				
			elif regxrp.group().lower() == 'gaus':
				pushkeydeclar('gaus', i, line, keywdtag, xde_lists, listaddrs)
	
			elif regxrp.group().lower() == 'mate':
				pushkeydeclar('mate', i, line, keywdtag, xde_lists, listaddrs)
				keywdtag['paragraph'] = 'AFmate'
				
			elif regxrp.group().lower() == 'shap':
				if keywdtag['shap'] == 0:
					listaddrs['shap'] = []
					xde_lists['shap'] = []
					keywdtag['shap'] = 1
				listaddrs['shap'].append(i)
				wordlist = line.strip().split()
				wordlist.pop(0)
				xde_lists['shap'].append(wordlist)
	
			elif regxrp.group().lower() == 'vect':
				pushcomdeclar('vect', i, line, keywdtag, xde_lists, listaddrs)

			elif regxrp.group().lower() == 'fmatr':
				pushcomdeclar('fmatr',i, line, keywdtag, xde_lists, listaddrs)
				
			elif regxrp.group().lower() == 'fvect':
				pushcomdeclar('fvect',i, line, keywdtag, xde_lists, listaddrs)

			elif regxrp.group().find('$')!= -1 or regxrp.group().find('@')!= -1:
				pushcommline (i, line, keywdtag, xde_lists, listaddrs)
				
			elif regxrp.group().lower() == 'mass':
				pushwekdeclar('mass', i, line, keywdtag, xde_lists, listaddrs)

			elif regxrp.group().lower() == 'damp':
				pushwekdeclar('damp', i, line, keywdtag, xde_lists, listaddrs)

			elif regxrp.group().lower() == 'stif':
				pushwekdeclar('stif', i, line, keywdtag, xde_lists, listaddrs)
				
			elif regxrp.group().lower() == 'dist':
				if keywdtag['paragraph'] == 'mass':
					xde_lists['mass'].append('dist')
					xde_lists['mass'].append(line.split('=')[1].strip())
				elif keywdtag['paragraph'] == 'damp':
					xde_lists['damp'].append('dist')
					xde_lists['damp'].append(line.split('=')[1].strip())
				elif keywdtag['paragraph'] == 'stif':
					xde_lists['stif'].append('dist')
					xde_lists['stif'].append(line.split('=')[1].strip())
					
			elif regxrp.group().lower() == 'load':
				if keywdtag['load'] == 0:
					xde_lists['load'] = []
				xde_lists['load'].append(line.split('=')[1].strip())
				keywdtag['paragraph'] = 'load'
			
			elif regxrp.group().lower() == 'func':
				wordlist = line.strip().split()
				if len(wordlist) != 1:
					if keywdtag['func'] == 0:
						xde_lists['func'] = []
					keywdtag['func'] = 1
					for j in range(2,len(wordlist)+1): xde_lists['func'].append(wordlist[j-1])
				else:
					keywdtag['paragraph'] = 'func'
					
			elif regxrp.group().lower() == 'matrix':
				pushcomdeclar('matrix', i, line, keywdtag, xde_lists, listaddrs)
				wordlist = line.strip().split()
				keywdtag['matrixname'] = wordlist[1]
				keywdtag['matrixtag'] = 1
	
			elif regxrp.group().lower() == 'end':
				print('reading end')

			else: print(str(line))