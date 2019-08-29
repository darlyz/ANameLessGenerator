#!/usr/bin/python
'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''

# key declare type1: DISP, COOR, SHAP, GAUS, MATE
def pushkeydeclar (ktag, strs, lnum, wlist, flist):
	if ktag[strs] != 0:
		print('warn: line {0}, duplicated declare, {1} has been declared at line {2}'.format(lnum,strs,ktag[strs]))
	else:
		ktag[strs] = lnum
		flist[strs] = []
		for j in range(2,len(wlist)+1): flist[strs].append(wlist[j-1])

# common declare type: VECT, FMATR	
def pushcomdeclar (ktag, strs, lnum, wlist, flist):
	if ktag[strs] == 0: 
		flist[strs] = {}
	ktag[strs] = lnum
	for j in range(2,len(wlist)+1):
		if j == 2: flist[strs][wlist[j-1]]=[]
		else: flist[strs][wlist[1]].append(wlist[j-1])

# common line : @L, @W, @A, $CC
def pushcommline (ktag, strs, lnum, wlist, flist):
	#if len(wlist) != 1:
	if ktag['mate'] == 0:
		newline = wlist[0]
		for j in range(1,len(wlist)): newline += ' '+wlist[j]
		flist['code']['BFmate'].append(newline)
	else:
		if ktag['func'] != 999:
			newline = wlist[0]
			for j in range(1,len(wlist)): newline += ' '+wlist[j]
			flist['code']['AFmate'].append(newline)
		else:
			newline = wlist[0]
			for j in range(1,len(wlist)): newline += ' '+wlist[j]
			flist['code']['INfunc'].append(newline)
			if   ktag['dist'] == 'stif' and ktag['stiftype'] == 1:
				newline = wlist[0]
				for j in range(1,len(wlist)): newline += ' '+wlist[j]
				flist['code']['INstif'].append(newline)
			elif ktag['dist'] == 'mass' and ktag['masstype'] == 1:
				newline = wlist[0]
				for j in range(1,len(wlist)): newline += ' '+wlist[j]
				flist['code']['INmass'].append(newline)
			elif ktag['dist'] == 'damp' and ktag['damptype'] == 1:
				newline = ''
				for j in range(1,len(wlist)): newline += ' '+wlist[j]
				flist['code']['INdamp'].append(newline)

# stif, mass, damp declare
def pushwekdeclar (ktag, strs, lnum, wlist, flist):
	if ktag[strs] != 0:
		print('error: line {0}, duplicated declare, {1} has been declared at line {2}'.format(lnum,strs,ktag[strs]))
		#break
	else:
		ktag[strs] = lnum
		flist[strs] = []
		if len(wlist) != 1:
			for j in range(2,len(wlist)+1):
				flist[strs].append(wlist[j-1])
		else:
			ktag[strs+'type'] = 1
			ktag['dist'] = strs

def parse_xde(fdename,list,keywdtag,fdelist,regkeyws):
	import re as regx
	
	#fdename = 'delxyz'
	file = open(fdename+'.fde', mode='r')
	for line in file.readlines():
		line = line.strip(' ')
		list.append(line)
	file.close()
	
	#for i in range(len(list)):
	#	print (list[i])
	
	#keywords = ['DISP', 'COOR', 'SHAP', 'GAUS', 'MATE', 'MASS', 'DAMP', 'STIF', 'COEF', \
	#			'VECT', 'FUNC', 'FMATR', 'MATRIX', '\$CC', '\$CP', '\$CV', '@L', '@W', '@A', \
	#			'DIST', 'LOAD']

	i = 0
	stitchline = ''
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
			line = line.split('//')[0]
		
		# retrieve the keywords
		regxrp = regx.search(regkeyws,line,regx.I)
		if regxrp == None:
			if line.find('[')!= -1 and line.find(']')!= -1:
				if keywdtag['dist'] == 'mass':
					fdelist['mass'].append(line.strip())
				elif keywdtag['dist'] == 'damp':
					fdelist['damp'].append(line.strip())
				elif keywdtag['dist'] == 'stif':
					fdelist['stif'].append(line.strip())
				elif keywdtag['dist'] == 'load':
					fdelist['load'].append(line.strip())
			elif keywdtag['matrixtag'] != 0 :
				if line.find('[')!= -1 or line.find(']')!= -1 :
					print('error: line {}, weak item is not allow to be contained in a matrix'.format(i))
				else:
					fdelist['matrix'][keywdtag['matrixname']].append(line.strip())
			else:
				print('redundant information or wrong declare, line {}: '.format(i)+line)
		elif regxrp.span()[0] != 0:
			keywdtag['matrixtag'] = 0
			print('error: line {0}, keyword {1} must be at the head of line.'.format(i,regxrp.group()))
			#break
		else:
			keywdtag['matrixtag'] = 0
			wordlist = line.strip().split()

			if   regxrp.group().lower() == 'disp':
				pushkeydeclar(keywdtag, 'disp', i, wordlist, fdelist)
	
			elif regxrp.group().lower() == 'coor':
				pushkeydeclar(keywdtag, 'coor', i, wordlist, fdelist)
	
			elif regxrp.group().lower() == 'shap':
				pushkeydeclar(keywdtag, 'shap', i, wordlist, fdelist)
	
			elif regxrp.group().lower() == 'gaus':
				pushkeydeclar(keywdtag, 'gaus', i, wordlist, fdelist)
	
			elif regxrp.group().lower() == 'mate':
				pushkeydeclar(keywdtag, 'mate', i, wordlist, fdelist)
	
			elif regxrp.group().lower() == 'vect':
				pushcomdeclar(keywdtag, 'vect', i, wordlist, fdelist)
		
			elif regxrp.group().lower() == 'fmatr':
				pushcomdeclar(keywdtag, 'fmatr',i, wordlist, fdelist)
					
			elif regxrp.group().lower() == '@l':
				pushcommline (keywdtag, 'optr', i, wordlist, fdelist)
					
			elif regxrp.group().lower() == '@w':
				pushcommline (keywdtag, 'oprw', i, wordlist, fdelist)
					
			elif regxrp.group().lower() == '@a':
				pushcommline (keywdtag, 'opra', i, wordlist, fdelist)
					
			elif regxrp.group().lower() == '$cc':
				pushcommline (keywdtag, 'code', i, wordlist, fdelist)

			elif regxrp.group().lower() == 'mass':
				pushwekdeclar(keywdtag, 'mass', i, wordlist, fdelist)
						
			elif regxrp.group().lower() == 'damp':
				pushwekdeclar(keywdtag, 'damp', i, wordlist, fdelist)
						
			elif regxrp.group().lower() == 'stif':
				pushwekdeclar(keywdtag, 'stif', i, wordlist, fdelist)
						
			elif regxrp.group().lower() == 'dist':
				if keywdtag['dist'] == 'mass':
					fdelist['mass'].append('dist')
					fdelist['mass'].append(line.split('=')[1].strip())
				elif keywdtag['dist'] == 'damp':
					fdelist['damp'].append('dist')
					fdelist['damp'].append(line.split('=')[1].strip())
				elif keywdtag['dist'] == 'stif':
					fdelist['stif'].append('dist')
					fdelist['stif'].append(line.split('=')[1].strip())
					
			elif regxrp.group().lower() == 'load':
				if keywdtag['load'] == 0:
					fdelist['load'] = []
				fdelist['load'].append(line.split('=')[1].strip())
				keywdtag['dist'] = 'load'
				
			elif regxrp.group().lower() == 'func': #.......
				if len(wordlist) != 1:
					if keywdtag['func'] == 0:
						fdelist['func'] = []
					keywdtag['func'] = 1
					for j in range(2,len(wordlist)+1): fdelist['func'].append(wordlist[j-1])
				else:
					keywdtag['func'] = 999

			elif regxrp.group().lower() == 'matrix':
				pushcomdeclar(keywdtag, 'matrix', i, wordlist, fdelist)
				keywdtag['matrixname'] = wordlist[1]
				keywdtag['matrixtag'] = 1
	
			elif regxrp.group().lower() == 'end':
				print('reading end')

			else: print(str(wordlist))