'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-19
 Author: Zhang_Licheng
 Title: complex tensor expression in dummy index summation
 All rights reserved
'''
import re as regx

#   (a+b)*c --> ['(','a','+','b',')','*','c']
def expr2list (expr):

	expr_list = []
	var = ''
	for i in range(len(expr)):
	
		if expr[i] == '+' or expr[i] == '-' \
		or expr[i] == '*' or expr[i] == '/' :
			if expr[i-1] != ')':
				expr_list.append(var)
			expr_list.append(expr[i])
			var = ''
			
		elif expr[i] == '(':
			expr_list.append(expr[i])
			
		elif expr[i] == ')':
			if expr[i-1] != ')':
				expr_list.append(var)
			expr_list.append(expr[i])
			
		else:
			var += expr[i]
			
	if expr[len(expr) - 1] != ')':
		expr_list.append(var)

	return expr_list
# end expr2list()


# ['a','*','b','/','c'] -->         expr2:'/'   --> return head order: 2
#  'a*b/c'                         /     \
#                             expr1:'*'   c
#                            /     \
#                           a       b
def parsing_equal_grade_opr(expr_list,expr_dict,opr_list,expr_order):
	
	expr_i = expr_order
	expr_name = ''
	for i in range(len(expr_list)):
		
		for strs in opr_list:
			if expr_list[i] == strs:
		
				expr_i += 1
				expr_name = 'expr_'+str(expr_i)
				expr_dict[expr_name] = {}
				expr_dict[expr_name]['opr']  = expr_list[i]
				if i > 2:
					for strr in opr_list:
						if expr_list[i] == strr:
							expr_dict[expr_name]['left'] = 'expr_'+str(expr_i-1)
				else:
					expr_dict[expr_name]['left'] = expr_list[i-1]
				expr_dict[expr_name]['righ'] = expr_list[i+1]
			
	return expr_i
# end parsing_equal_grade_opr()


# ['a','-','b','*','c'] -->   expr2:'-'         --> return head order: 2
#  'a-b*c'                   /     \ 
#                           a      expr1:'*'
#                                 /     \ 
#                                b       c
def parsing_unequal_grade_opr(expr_list,expr_dict,opr_lists,expr_order):
	
	expr_i = expr_order
	for oprlist_i in range(len(opr_lists)):
	
		opr_list = opr_lists[oprlist_i]
		upper_expr_lists = []
		upper_expr_locat = []
		upper_expr_i = 0
		
		# draw the upper grade operator expression
		list_i = 0
		for strs in expr_list:
		
			for opr_str in opr_list:
				if strs == opr_str:
				
					upper_start_tag = 0
					if   list_i == 1 :
						upper_start_tag = 0
					elif list_i >  2 :
						for opr_str1 in opr_list:
							if expr_list[list_i-2] == opr_str1:
								upper_start_tag += 1
					if upper_start_tag == 0:
						upper_expr_lists.append([])
						upper_expr_locat.append([])
						upper_expr_i += 1
							
					upper_expr_lists[upper_expr_i-1].append(expr_list[list_i-1])
					upper_expr_lists[upper_expr_i-1].append(expr_list[list_i])
					upper_expr_locat[upper_expr_i-1].append(list_i-1)
					upper_expr_locat[upper_expr_i-1].append(list_i)
					
					upper_end_tag = 0
					if   list_i == len(expr_list) - 2:
						upper_end_tag = 0
					elif list_i <  len(expr_list) - 3:
						for opr_str1 in opr_list:
							if expr_list[list_i+2] == opr_str1:
								upper_end_tag += 1
					if upper_end_tag ==0:
						upper_expr_lists[upper_expr_i-1].append(expr_list[list_i+1])
						upper_expr_locat[upper_expr_i-1].append(list_i+1)
			
			list_i += 1
		
		# parsing the upper grade operator expression and replace them in expr_list
		list_i = 0
		for upper_list in upper_expr_lists:
		
			# parsing
			expr_i = parsing_equal_grade_opr(upper_list,expr_dict,opr_list,expr_i)
			
			# replacing
			upper_locat = upper_expr_locat[list_i]
			for locat_i in range(len(upper_locat)):
				if locat_i == 0:
					expr_list[int(upper_locat[locat_i])] = 'expr_'+str(expr_i)
				else:
					expr_list[int(upper_locat[locat_i])] = ''
			list_i += 1
		
		# replacing
		temp_list = expr_list.copy()
		expr_list.clear()
		for strs in temp_list:
			if strs != '':
				expr_list.append(strs)
	
	return expr_i
# end parsing_unequal_grade_opr()


# ['a','*','(','b','-','c','/','d') -->   expr3:'*'       --> return head order: 3
#  'a*(b-c/d)'                           /     \ 
#                                       a      expr2:'-'
#                                             /     \ 
#                                            b      expr1:'/'
#                                                  /     \
#                                                 c       d
def parsing_with_bracket_opr(expr_list,expr_dict,opr_lists,expr_order):
	
	expr_i = expr_order
	
	# count the max level of bracket
	bracket_tag = 0
	max_bracket_level   = 0
	for strs in expr_list:	
		if strs == '(':
			bracket_tag += 1
		elif strs == ')':
			bracket_tag -= 1
				
		if  max_bracket_level < bracket_tag:
			max_bracket_level = bracket_tag
	
	
	for level in reversed(range(1,max_bracket_level+1)):
		
		# locate the bracket
		bracket_tag = 0
		left_bracket_locat = []
		righ_bracket_locat = []
		list_i = 0
		for strs in expr_list:
		
			if   strs == '(':
				bracket_tag += 1
				if bracket_tag == level:
					left_bracket_locat.append(list_i)
					
			elif strs == ')':
				if bracket_tag == level:
					righ_bracket_locat.append(list_i)
				bracket_tag -= 1
				
			list_i += 1
			
		# draw expression in bracket, parsing and replace them
		bracket_expr = []
		for bracket_i in range(len(righ_bracket_locat)):
		
			bracket_expr.append([])
			
			for kk in range(left_bracket_locat[bracket_i]+1, \
							righ_bracket_locat[bracket_i]):			
				bracket_expr[bracket_i].append(expr_list[kk])
			
			# parsing bracket expression
			expr_i = parsing_unequal_grade_opr(bracket_expr[bracket_i],expr_dict,opr_lists,expr_i)
			
			# replace the bracket expression in expr_list
			for kk in range(left_bracket_locat[bracket_i], \
							righ_bracket_locat[bracket_i]+1):
				if kk == left_bracket_locat[bracket_i]:
					expr_list[kk] = 'expr_'+str(expr_i)
				else:
					expr_list[kk] = ''
		
		# replace the bracket expression in expr_list
		temp_list = expr_list.copy()
		expr_list.clear()
		for strs in temp_list:
			if strs != '':
				expr_list.append(strs)
					
	expr_i = parsing_unequal_grade_opr(expr_list,expr_dict,opr_lists,expr_i)
	
	return expr_i
# end parsing_with_bracket_opr()

# ---------------------------------------------------------------------------------------------------------------------------

# [a1,a2,..] opr [b1,b2,...] --> [a1 opr b1, a2 opr b2, ...]
# [a1,a2,..] opr b           --> [a1 opr b,  a2 opr b,  ...], opr: + - * /
# b opr [a1,a2,..]           --> [b  opr a1, b  opr a2, ...]
# follow as max size law : [a1,a2] opr [b1,b2,b3] --> [a1 opr b1,a2 opr b2,x opr b3], x=1 when opr = '*''/', x=0 when opr = '+''-'
def vector_opr(left,righ,opr_str):

	vector_list = []
	
	if righ == '':
		opr = ''

	if  isinstance(left,list) \
	and isinstance(righ,list) :
	
		if  len(left) == 0 \
		and len(righ) == 0 :
			return []
			
		if (len(left) != 0 and not isinstance(left[0],str)) \
		or (len(righ) != 0 and not isinstance(righ[0],str)) :
			return []
	
		left_len = len(left)
		righ_len = len(righ)
		max_len  = left_len if left_len > righ_len else righ_len
		min_len  = left_len if left_len < righ_len else righ_len
		
		for ii in range(max_len):
		
			left_str = left[ii] if ii < left_len else ''
			righ_str = righ[ii] if ii < righ_len else ''
			
			if opr_str == '/' and left_str == '':
				left_str = '1'
				opr = opr_str
			elif opr_str == '-' and left_str == '':
				opr = opr_str
			else:
				opr  = opr_str if ii < min_len else ''
				
			if righ_str == '':
				opr = ''
			
			vector_list.append(left_str+opr+righ_str)

	elif isinstance(left,list) and len(left) != 0 \
    and  isinstance(righ,str) :

		if isinstance(left[0],str) :
			for ii in range(len(left)):
				vector_list.append(left[ii]+opr_str+righ)
		
	elif isinstance(left,str) \
	and  isinstance(righ,list) and len(righ) != 0 :
	
		if isinstance(righ[0],str) :
			for ii in range(len(righ)):
				vector_list.append(left+opr_str+righ[ii])
		
	else:
		return []

	return vector_list
# end vector_opr()
	
# [a1,a2,..] * [b1,b2,...]^T -->  a1*b1 + a2*b2 + ...
# follow as min size law : [a1,a2,a3] * [b1,b2]^T --> a1*b1+a2*b2
# and right item is considered as Transposition
def vector_dot_multiply(left,righ):

	opr = '*'

	if  isinstance(left,list) and len(left) !=0 and isinstance(left[0],str) \
	and isinstance(righ,list) and len(righ) !=0 and isinstance(righ[0],str) :
		left_len = len(left)
		righ_len = len(righ)
		min_len  = left_len if left_len < righ_len else righ_len
		
		if righ[0] == '':
			opr = ''
		
		scalar_strs = left[0]+opr+righ[0]
		for ii in range(1,min_len):
		
			if righ[ii] == '':
				opr = ''
			scalar_strs += '+'+left[ii]+opr+righ[ii]
	
		return scalar_strs
		
	else:
		return ''
# end vector_dot_multiply()

# [[a11, a12, ...]       ]     [[b11, b12, ...]       ]     [[a11 opr b11, a12 opr b12, ...]       ]
# [[a21, a22, ...]       ]     [[b21, b22, ...]       ]     [[a21 opr b21, a22 opr b22, ...]       ]
# [[a31, a32, ...] , ... ] opr [[b31, b32, ...] , ... ] --> [[a31 opr b31, a32 opr b32, ...] , ... ]  , opr: + - * /
# [ ...                  ]     [ ...                  ]     [ ...                                  ]
# [ ...                  ]     [ ...                  ]     [ ...                                  ]
# -------------------------------------------------------------------------------------------------------------------
# [[a11, a12, ...]       ]           [[a11 opr b, a12 opr b, ...]       ]
# [[a21, a22, ...]       ]           [[a21 opr b, a22 opr b, ...]       ]
# [[a31, a32, ...] , ... ] opr b --> [[a31 opr b, a32 opr b, ...] , ... ] or b is at left
# [ ...                  ]           [ ...                              ]
# [ ...                  ]           [ ...                              ]
# follow as max size law
def tensor_opr(left,righ,opr_str):
	
	tensor_list = []
	
	if  isinstance(left,list) \
	and isinstance(righ,list) :

		left_len = len(left)
		righ_len = len(righ)
		max_len  = left_len if left_len > righ_len else righ_len

		if  isinstance(left[0],list) \
		and isinstance(righ[0],list):

			for ii in range(max_len):
	
				if   isinstance(left[0][0],str):
					left_list = left[ii].copy() if ii < left_len else []
				elif isinstance(left[0][0],list):
					left_list = left[ii].copy()
	
				if   isinstance(righ[0][0],str):
					righ_list = righ[ii].copy() if ii < righ_len else []
				elif isinstance(righ[0][0],list):
					righ_list = righ[ii].copy()
	
				if  isinstance(left[0][0],str) \
				and isinstance(righ[0][0],str):
					tensor_list.append(vector_opr(left_list,righ_list,opr_str))
				else:
					tensor_list.append(tensor_opr(left_list,righ_list,opr_str))

		elif isinstance(left[0],str) \
		and  isinstance(righ[0],list):

			for ii in range(righ_len):
				righ_list = righ[ii].copy()
				if isinstance(righ[0][0],list):
					tensor_list.append(tensor_opr(left,righ_list,opr_str))
				elif isinstance(righ[0][0],str):
					tensor_list.append(vector_opr(left,righ_list,opr_str))

		elif isinstance(left[0],list) \
		and  isinstance(righ[0],str):

			for ii in range(left_len):
				left_list = left[ii].copy()
				if isinstance(left[0][0],list):
					tensor_list.append(tensor_opr(left_list,righ,opr_str))
				elif isinstance(left[0][0],str):
					tensor_list.append(vector_opr(left_list,righ,opr_str))

		elif isinstance(left[0],str) \
		and  isinstance(righ[0],str):
			tensor_list = vector_opr(left,righ,opr_str)
	
	elif isinstance(left,str) \
	and  isinstance(righ,list):

		if isinstance(righ[0],str):
			tensor_list = vector_opr(left,righ,opr_str)

		elif isinstance(righ[0],list):

			for ii in range(len(righ)):
				if isinstance(righ[0][0],str):
					tensor_list.append(vector_opr(left,righ[ii],opr_str))
				elif isinstance(righ[0][0],list):
					tensor_list.append(tensor_opr(left,righ[ii],opr_str))

	elif isinstance(left,list) \
	and  isinstance(righ,str):

		if isinstance(left[0],str):
			tensor_list = vector_opr(left,righ,opr_str)

		elif isinstance(left[0],list):

			for ii in range(len(left)):
				if isinstance(left[0][0],str):
					tensor_list.append(vector_opr(left[ii],righ,opr_str))
				elif isinstance(left[0][0],list):
					tensor_list.append(tensor_opr(left[ii],righ,opr_str))

	elif isinstance(left,str) \
	and  isinstance(righ,str) :
		return left+opr_str+righ

	return tensor_list
# tensor_opr()

# [a11,a12] * [b11,b21]^T --> [a11*b11+a12*b21, a11*b12+a12*b22]
# [a21,a22]	  [b12,b22]       [a21*b11+a22*b21, a21*b12+a22*b22]
# ------------------------------------------------------------
# [a11,a12] * [b1,b2]^T --> [a11*b1+a12*b2, a21*b1+a22*b2]
# [a21,a22]
# follow as min size law, and right item is considered as Transposed
def matrix_multiply(left,righ):
	matrix_list = []
	vector_list = []
	
	if  isinstance(left,list) \
	and isinstance(righ,list) :

		# M · M
		if  isinstance(left[0],list) \
		and isinstance(righ[0],list) :
			if  isinstance(left[0][0],str) \
			and isinstance(righ[0][0],str) :

				for ii in range(len(righ)):
					matrix_list.append([])
					for jj in range(len(left)):
						matrix_list[ii].append(vector_dot_multiply(left[ii],righ[jj]))		
				return matrix_list
			else:
				return None

		# M · V
		elif isinstance(left[0],list) \
		and  isinstance(righ[0],str) :
			if  isinstance(left[0][0],str) :

				for ii in range(len(left)):
					vector_list.append(vector_dot_multiply(left[ii],righ))
				return vector_list
			else:
				return None

		# V · M
		elif isinstance(left[0],str) \
		and  isinstance(righ[0],list) :
			if isinstance(righ[0][0],str) :

				for ii in range(len(righ)):
					vector_list.append(vector_dot_multiply(left,righ[ii]))
				return vector_list
			else:
				return None

		# V · V
		elif isinstance(left[0],str) \
		and  isinstance(righ[0],str) :
			return vector_dot_multiply(left,righ)

		else:
			return None

	elif isinstance(left,list) \
	and  isinstance(righ,str) :

		# M · S
		if isinstance(left[0],list) :
			if isinstance(left[0][0],str) :

				for ii in range(len(left)) :
					matrix_list.append(vector_opr(left[ii],righ,'*'))
				return matrix_list
			else:
				return None

		# V · S
		elif isinstance(left[0],str) :
			return vector_opr(left,righ,'*')

		else:
			return None

	elif isinstance(left,str) \
	and  isinstance(righ,list) :

		# S · M
		if isinstance(righ[0],list) :
			if isinstance(righ[0][0],str) :

				for ii in range(len(righ)) :
					matrix_list.append(vector_opr(left,righ[ii],'*'))
				return matrix_list
			else:
				return None

		# S · V
		elif isinstance(righ[0],str) :
			return vector_opr(left,righ,'*')

		else:
			return None
	# S · S
	elif isinstance(left,str) \
	and  isinstance(righ,str) :

		return left+'*'+righ

	else:
		return None
# end matrix_multiply()

# follw as left move law: [a11,a12]         [a11,a21]
#                         [a21,a22,a23] --> [a12,a22]
#                                           [a23]
def matrix_transpose(matrix):
	tran_matrix = []
	max_len = 0

	if isinstance(matrix,str):
		return matrix
	elif isinstance(matrix,list) \
	and  isinstance(matrix[0],str):
		for ii in range(len(matrix)):
			tran_matrix.append([])
			tran_matrix[ii].append(matrix[ii])
		return tran_matrix
	elif isinstance(matrix,list) \
	and  isinstance(matrix[0],list) \
	and  isinstance(matrix[0][0],str) :
		for ii in range(len(matrix)):
			max_len = max_len if max_len > len(matrix[ii]) else len(matrix[ii])
		
		for ii in range(max_len):
			tran_matrix.append([])
			for jj in range(len(matrix)):
				if ii < len(matrix[jj]):
					tran_matrix[ii].append(matrix[jj][ii])
				
		return tran_matrix
	else:
		return None
# end matrix_inverse()

def vector_add_bracket(vector_list):
	temp_list = []
	for strs in vector_list:
		temp_list.append('('+strs+')')
	return temp_list
# end vector_add_bracket()
	
def tensor_add_bracket(tensor_list):
	temp_list = []
	if  isinstance(tensor_list,list) \
	and isinstance(tensor_list[0],str) :
		temp_list = vector_add_bracket(tensor_list)
	elif isinstance(tensor_list,list) \
	and  isinstance(tensor_list[0],list) :
		for alist in tensor_list:
			temp_list.append(tensor_add_bracket(alist))
	return temp_list
# end tensor_add_bracket()

# calculate tensor expression directly without dummy index
# note: do not use it after matrix_expr() or make a copy of expr_dict befor matrix_expr()
def tensor_expr(expr_head,expr_dict):

	tensor_list = []
	expr_sub  = ''

	for strs in ['left','righ']:
		if not isinstance(expr_dict[expr_head][strs],list) \
		and expr_dict[expr_head][strs].find('expr') != -1:
			
			expr_sub = expr_dict[expr_head][strs]
			expr_dict[expr_head][strs] = tensor_expr(expr_sub,expr_dict)
			
			if  (expr_dict[expr_head]['opr'] == '*' \
			or   expr_dict[expr_head]['opr'] == '/') \
			and (expr_dict[expr_sub ]['opr'] == '+' \
			or   expr_dict[expr_sub ]['opr'] == '-') :
				expr_dict[expr_head][strs] = tensor_add_bracket(expr_dict[expr_head][strs])

	tensor_list = tensor_opr(expr_dict[expr_head]['left'], \
							 expr_dict[expr_head]['righ'], \
							 expr_dict[expr_head]['opr'])

	return tensor_list
# end tensor_expr()

def tensor_summation(tensor_list):
	expr_strs = ''

	if  isinstance(tensor_list,list) \
	and isinstance(tensor_list[0],str) :
		for strs in tensor_list:
			expr_strs += strs+'+'
		expr_strs = expr_strs.rstrip('+')
	elif isinstance(tensor_list,list) \
	and  isinstance(tensor_list[0],list) :
		for alist in tensor_list:
			expr_strs += tensor_summation(alist)+'+'
		expr_strs = expr_strs.rstrip('+')

	return expr_strs
# end tensor_summation()

def tensor_production(tensor_list):
	expr_strs = ''

	if  isinstance(tensor_list,list) \
	and isinstance(tensor_list[0],str) :
		for strs in tensor_list:
			expr_strs += '('+strs+')'+'*'
		expr_strs = expr_strs.rstrip('*')
	elif isinstance(tensor_list,list) \
	and  isinstance(tensor_list[0],list) :
		for alist in tensor_list:
			expr_strs += tensor_production(alist)+'*'
		expr_strs = expr_strs.rstrip('*')

	return expr_strs
# end tensor_production()

# calculate expression contained matrix vector and scalar without dummy index
# note: do not use it after tensor_expr() or make a copy of expr_dict befor tensor_expr()
def matrix_expr(expr_head,expr_dict):
	matrix_list = []
	expr_sub  = ''

	for strs in ['left','righ']:
		if not isinstance(expr_dict[expr_head][strs],list) \
		and expr_dict[expr_head][strs].find('expr') != -1:

			expr_sub = expr_dict[expr_head][strs]
			expr_dict[expr_head][strs] = matrix_expr(expr_sub,expr_dict)

			if  (expr_dict[expr_head]['opr'] == '*' \
			or   expr_dict[expr_head]['opr'] == '/') \
			and (expr_dict[expr_sub ]['opr'] == '+' \
			or   expr_dict[expr_sub ]['opr'] == '-' \
			or   expr_dict[expr_sub ]['opr'] == '*') :
				expr_dict[expr_head][strs] = tensor_add_bracket(expr_dict[expr_head][strs])
		
	if expr_dict[expr_head]['opr'] == '*' :
		#print(expr_head)
		matrix_list = matrix_multiply(expr_dict[expr_head]['left'], \
									  expr_dict[expr_head]['righ'])
	else:
		#print(expr_head)
		matrix_list = tensor_opr(expr_dict[expr_head]['left'], \
								 expr_dict[expr_head]['righ'], \
								 expr_dict[expr_head]['opr'])

	return matrix_list
# end matrix_expr()

# transform a_i_j to list in expr_dict and save the dummy index
def trans_tensor_expr_list(expr_dict,xde_lists):

	for expr_key in expr_dict.keys():
		for item in ['left','righ']:
			if not isinstance(expr_dict[expr_key][item],list) \
			and expr_dict[expr_key][item].find('expr') == -1:

				items_list = expr_dict[expr_key][item].split('_')
				var_name   = items_list[0]

				if len(items_list) > 1:
					expr_dict[expr_key][item] = var_name
					
					idx_i = 0
					for idx in items_list:
						if idx_i == 0:
							expr_dict[expr_key][item+'_indx'] = []
						else:
							expr_dict[expr_key][item+'_indx'].append(idx)
						idx_i += 1
				
				# vector		
				if len(items_list) == 2:

					if 'vect' in xde_lists and var_name in xde_lists['vect']:
						expr_dict[expr_key][item] = xde_lists['vect'][var_name]
					if 'fvect' in xde_lists and var_name in xde_lists['fvect']:
						expr_dict[expr_key][item] = xde_lists['fvect'][var_name]

				# matrix
				elif len(items_list) == 3:

					if 'matrix' in xde_lists and var_name in xde_lists['matrix']:
						expr_dict[expr_key][item] = []
						for lists in xde_lists['matrix'][var_name]:
							expr_dict[expr_key][item].append(lists)

					if 'fmatr' in xde_lists and var_name in xde_lists['fmatr']:
						expr_dict[expr_key][item] = []
						for lists in xde_lists['fmatr'][var_name]:
							expr_dict[expr_key][item].append(lists)
				# scalar
				elif len(items_list) == 1:
					pass
				# tensor not defined
				else :
					print('not defined')
# end trans_tensor_expr_list()

# xde_tnsr --> xde_tnsr_list & tnsr_dict   return->
# a_i_j    --> [a,i,j]         {i:2,j:3}   [i,j]
def parse_xde_type_tensor(xde_tnsr,xde_tnsr_list,tnsr_dict,xde_lists):

	if xde_tnsr.find('_') != -1:
		for strs in xde_tnsr.split('_'):
			xde_tnsr_list.append(strs)

		if   len(xde_tnsr_list) == 2:
			tnsr_dict[xde_tnsr_list[1]] = len(xde_lists['vect'][xde_tnsr_list[0]])

		elif len(xde_tnsr_list) == 3:
			tnsr_dict[xde_tnsr_list[1]] = len(xde_lists['matrix'][xde_tnsr_list[0]])
			tnsr_dict[xde_tnsr_list[2]] = len(xde_lists['matrix'][xde_tnsr_list[0]][0])

		else: pass

	return list(tnsr_dict.keys())
# end parse_xde_type_tensor()

# transform "a_i_j" to "xde_lists['matrix']['a'][i][j]"
#           "a_i"   to "xde_lists['vect']['a'][i]"
def trans_xde_type_tensor(tnsr_indxs,var_list):

	if len(tnsr_indxs) == 1:
		tensor_tag = 'vect'
	elif len(tnsr_indxs) == 2:
		tensor_tag = 'matrix'

	tnsr_strs = ''
	tnsr_strs += 'xde_lists[\''+tensor_tag+'\']'
	tnsr_strs += '[\''+var_list[0]+'\']'

	for ii in range(len(tnsr_indxs)):
		tnsr_strs += '['+tnsr_indxs[ii]+']'
	
	return tnsr_strs
# end trans_xde_type_tensor()

def idx_summation(left_var,righ_expr,xde_lists):

	SAEfile = open('temppy.temp', mode='w')

	# expand the bracket
	# righ_expr = expand_expr(righ_expr)

	# write the self-auto-executing file
	SAEfile.write('import json\n')
	SAEfile.write('jsonfile = open(\'tempjson.temp\', mode=\'r\')\n')
	SAEfile.write('json_str = jsonfile.read()\n')
	SAEfile.write('xde_lists = json.loads(json_str)\n')
	SAEfile.write('jsonfile.close()\n\n')

	SAEfile.write('tempfile = open(\'tempexpr.temp\', mode=\'w\')\n')
	SAEfile.write('exprs={}\n')

	SAEfile.write('\n')

	# find left variable's indexs
	left_var_list = []
	left_idxlen = {}
	left_indxs  = parse_xde_type_tensor(left_var,left_var_list,left_idxlen,xde_lists)
	tnsr_xde_l  = trans_xde_type_tensor(left_indxs,left_var_list)

	# write "for i1 in range(n1): for i2 in range(n2): ..."
	left_indentation = ''
	for ii in range(len(left_indxs)):
		SAEfile.write(left_indentation+'for '+left_indxs[ii]+' in range('+str(left_idxlen[left_indxs[ii]])+'):\n')
		left_indentation += '\t'

	# write "exprs[str(i1)+str(i2)+...] = xde_lists['vect/matrix']['a'][i1][i2]..."
	temp_expr_key = ''
	for ii in range(len(left_indxs)):
		temp_expr_key += '+str('+left_indxs[ii]+')'
	temp_expr_key = temp_expr_key.lstrip('+')
	left_item = 'exprs['+temp_expr_key+']'
	SAEfile.write(left_indentation+left_item+' = ')

	SAEfile.write(tnsr_xde_l+'+\'=\'')

	SAEfile.write('\n')

	# split expr to list by the lowest priority
	righ_expr_list = []
	bracket_count  = 0
	expr_left_addr = 0
	expr_righ_addr = 0
	for ii in range(len(righ_expr)):
		if righ_expr[ii] == '(':
			bracket_count += 1
		elif righ_expr[ii] == ')':
			bracket_count -= 1

		if ((righ_expr[ii] == '+' \
		or righ_expr[ii] == '-') \
		and bracket_count == 0) \
		or ii == len(righ_expr)-1:
			if ii == len(righ_expr)-1:
				expr_righ_addr = ii+1
			else:
				expr_righ_addr = ii
			righ_expr_list.append(righ_expr[expr_left_addr:expr_righ_addr])
			expr_left_addr = expr_righ_addr


	for expr_strs in righ_expr_list:
		
		# find tensors in right expression
		righ_idxlen = {}
		righ_indxs  = []
		pattern = regx.compile(r'[a-zA-Z]+(?:_[a-zA-Z])+')
		tensor_list = pattern.findall(expr_strs)
	
		# find indexs in right expression and pop non-repetitive tensors and indexs
		temp_list  = []
		for strs in tensor_list:

			if temp_list.count(strs) == 0:
				temp_list.append(strs)

			temp_idxsl = strs.split('_')

			if   len(temp_idxsl) == 2:
				if not temp_idxsl[1] in left_idxlen:
					righ_idxlen[temp_idxsl[1]] = len(xde_lists['vect'][temp_idxsl[0]])

			elif len(temp_idxsl) == 3:
				if not temp_idxsl[1] in left_idxlen:
					righ_idxlen[temp_idxsl[1]] = len(xde_lists['matrix'][temp_idxsl[0]])
				if not temp_idxsl[2] in left_idxlen:
					righ_idxlen[temp_idxsl[2]] = len(xde_lists['matrix'][temp_idxsl[0]][0])

			else: pass

		tensor_list = temp_list.copy()
		righ_indxs = list(righ_idxlen.keys())

		righ_indentation = left_indentation
		for ii in range(len(righ_indxs)):
			SAEfile.write(righ_indentation+'for '+righ_indxs[ii]+' in range('+str(righ_idxlen[righ_indxs[ii]])+'):\n')
			righ_indentation += '\t'

		SAEfile.write(righ_indentation+left_item+' += ')

		def tran_index(matched):
			tnsr_strs = matched.group('index')
			tnsr_list = tnsr_strs.split('_')

			tensor_tag = ''
			if len(tnsr_list) == 2:
				tensor_tag = 'vect'
			elif len(tnsr_list) == 3:
				tensor_tag = 'matrix'

			tnsr_strs = ''
			tnsr_strs += 'xde_lists[\''+tensor_tag+'\']'
			tnsr_strs += '[\''+tnsr_list[0]+'\']'

			for ii in range(1,len(tnsr_list)):
				tnsr_strs += '['+tnsr_list[ii]+']'
	
			return '\'+'+tnsr_strs+'+\''

		expr_strs = regx.sub(r'(?P<index>([a-zA-Z]+(?:_[a-zA-Z])+))',tran_index,expr_strs)

		SAEfile.write('\''+expr_strs+'\'')

		SAEfile.write('\n')

	SAEfile.write('\nfor strs in exprs.keys():\n')
	SAEfile.write('\ttempfile.write(exprs[strs]+\'\\n\')\n')
	SAEfile.write('tempfile.close()\n')

	SAEfile.close()

	import json
	tempjson = {}
	tempjson['vect']=xde_lists['vect']
	tempjson['matrix']=xde_lists['matrix']
	file = open('tempjson.temp',mode='w')
	file.write(json.dumps(tempjson,indent=4))
	file.close()

	import os
	import platform 
	osinfo = platform.system()
	if osinfo == 'Windows':
		del_wds = 'del'
	elif osinfo == 'Linux':
		del_wds = 'rm'

	os.system('python temppy.temp')
	os.system(del_wds+' temppy.temp')
	os.system(del_wds+' tempjson.temp')

	exprfile = open('tempexpr.temp',mode='r')
	expr_strs = exprfile.read()
	exprfile.close()

	os.system(del_wds+' tempexpr.temp')

	return expr_strs
# end idx_summation()

def idx_summation_lua(left_var,righ_expr,xde_lists):

	SAEfile = open('templua.temp', mode='w')

	# expand the bracket
	# righ_expr = expand_expr(righ_expr)

	# write the self-auto-executing file
	SAEfile.write('xde_lists = {}\n')
	for strs in ['vect','matrix']:
		if strs in xde_lists:
			vect_str = 'xde_lists[\''+strs+'\']'
			SAEfile.write(vect_str+'={}\n')
			for keys in xde_lists[strs].keys():
				SAEfile.write(vect_str+'[\''+keys+'\']='+str(xde_lists[strs][keys]).replace('[','{').replace(']','}')+'\n')

	SAEfile.write('tempfile = io.open(\'tempexpr.temp\', \'w\')\n')
	SAEfile.write('exprs={}\n')

	SAEfile.write('\n')

	# find left variable's indexs
	left_var_list = []
	left_idxlen = {}
	left_indxs  = parse_xde_type_tensor(left_var,left_var_list,left_idxlen,xde_lists)
	tnsr_xde_l  = trans_xde_type_tensor(left_indxs,left_var_list)

	# write "for i1=1,n1 do for i2=1,n2 do ..."
	left_indentation = ''
	for ii in range(len(left_indxs)):
		SAEfile.write(left_indentation+'for '+left_indxs[ii]+'=1,'+str(left_idxlen[left_indxs[ii]])+' do\n')
		left_indentation += '\t'

	# write "exprs[tostring(i1)+tostring(i2)+...] = xde_lists['vect/matrix']['a'][i1][i2]..."
	temp_expr_key = ''
	for ii in range(len(left_indxs)):
		temp_expr_key += '+tostring('+left_indxs[ii]+')'
	temp_expr_key = temp_expr_key.lstrip('+')
	left_item = 'exprs['+temp_expr_key+']'
	SAEfile.write(left_indentation+left_item+' = ')

	SAEfile.write(tnsr_xde_l+'..\'=\'')

	SAEfile.write('\n')

	# split expr to list by the lowest priority
	righ_expr_list = []
	bracket_count  = 0
	expr_left_addr = 0
	expr_righ_addr = 0
	for ii in range(len(righ_expr)):
		if righ_expr[ii] == '(':
			bracket_count += 1
		elif righ_expr[ii] == ')':
			bracket_count -= 1

		if ((righ_expr[ii] == '+' \
		or righ_expr[ii] == '-') \
		and bracket_count == 0) \
		or ii == len(righ_expr)-1:
			if ii == len(righ_expr)-1:
				expr_righ_addr = ii+1
			else:
				expr_righ_addr = ii
			righ_expr_list.append(righ_expr[expr_left_addr:expr_righ_addr])
			expr_left_addr = expr_righ_addr


	for expr_strs in righ_expr_list:
		
		# find tensors in right expression
		righ_idxlen = {}
		righ_indxs  = []
		pattern = regx.compile(r'[a-zA-Z]+(?:_[a-zA-Z])+')
		tensor_list = pattern.findall(expr_strs)
	
		# find indexs in right expression and pop non-repetitive tensors and indexs
		temp_list  = []
		for strs in tensor_list:

			if temp_list.count(strs) == 0:
				temp_list.append(strs)

			temp_idxsl = strs.split('_')

			if   len(temp_idxsl) == 2:
				if not temp_idxsl[1] in left_idxlen:
					righ_idxlen[temp_idxsl[1]] = len(xde_lists['vect'][temp_idxsl[0]])

			elif len(temp_idxsl) == 3:
				if not temp_idxsl[1] in left_idxlen:
					righ_idxlen[temp_idxsl[1]] = len(xde_lists['matrix'][temp_idxsl[0]])
				if not temp_idxsl[2] in left_idxlen:
					righ_idxlen[temp_idxsl[2]] = len(xde_lists['matrix'][temp_idxsl[0]][0])

			else: pass

		tensor_list = temp_list.copy()
		righ_indxs = list(righ_idxlen.keys())

		righ_indentation = left_indentation
		for ii in range(len(righ_indxs)):
			SAEfile.write(righ_indentation+'for '+righ_indxs[ii]+'=1,'+str(righ_idxlen[righ_indxs[ii]])+' do\n')
			righ_indentation += '\t'

		SAEfile.write(righ_indentation+left_item+' = '+left_item+'..')

		def tran_index(matched):
			tnsr_strs = matched.group('index')
			tnsr_list = tnsr_strs.split('_')

			tensor_tag = ''
			if len(tnsr_list) == 2:
				tensor_tag = 'vect'
			elif len(tnsr_list) == 3:
				tensor_tag = 'matrix'

			tnsr_strs = ''
			tnsr_strs += 'xde_lists[\''+tensor_tag+'\']'
			tnsr_strs += '[\''+tnsr_list[0]+'\']'

			for ii in range(1,len(tnsr_list)):
				tnsr_strs += '['+tnsr_list[ii]+']'
	
			return '\'..'+tnsr_strs+'..\''

		expr_strs = regx.sub(r'(?P<index>([a-zA-Z]+(?:_[a-zA-Z])+))',tran_index,expr_strs)

		SAEfile.write('\''+expr_strs+'\'')

		SAEfile.write('\n')

		for ii in range(len(left_indentation),len(righ_indentation)):
			SAEfile.write((len(righ_indentation)-ii)*'\t'+'end\n')

	for ii in range(len(left_indentation)):
		SAEfile.write((len(left_indentation)-ii-1)*'\t'+'end\n')

	SAEfile.write('\nfor key,value in pairs(exprs) do\n')
	SAEfile.write('\ttempfile:write(value..\'\\n\')\n')
	SAEfile.write('end\n')
	SAEfile.write('tempfile:close()\n')

	SAEfile.close()

	import json
	tempjson = {}
	tempjson['vect']=xde_lists['vect']
	tempjson['matrix']=xde_lists['matrix']
	file = open('tempjson.temp',mode='w')
	file.write(json.dumps(tempjson,indent=4))
	file.close()

	import os
	import platform 
	osinfo = platform.system()
	if osinfo == 'Windows':
		del_wds = 'del'
	elif osinfo == 'Linux':
		del_wds = 'rm'

	os.system('lua templua.temp')
	os.system(del_wds+' templua.temp')

	exprfile = open('tempexpr.temp',mode='r')
	expr_strs = exprfile.read()
	exprfile.close()

	os.system(del_wds+' tempexpr.temp')

	return expr_strs
# end idx_summation_lua()

# transform 'a' to ['ar','ai'] in expr_dict
def trans_complex_expr_list(expr_dict):
	for keys in expr_dict.keys():
		for side in ['left','righ']:
			if expr_dict[keys][side].find('expr') == -1:
				var = expr_dict[keys][side]
				expr_dict[keys][side] = [var+'r',var+'i']
# end trans_complex_expr_list()

# expand complex expression
def complex_expr(expr_head,expr_dict):
	
	expr_sub = ''

	for strs in ['left','righ']:
		if not isinstance(expr_dict[expr_head][strs],list) \
		and expr_dict[expr_head][strs].find('expr') != -1:

			expr_sub = expr_dict[expr_head][strs]
			expr_dict[expr_head][strs] = complex_expr(expr_sub,expr_dict)

	left = expr_dict[expr_head]['left']
	righ = expr_dict[expr_head]['righ']

	if expr_dict[expr_head]['opr'] == '+' :
		return complex_add(left,righ)
	elif expr_dict[expr_head]['opr'] == '-' :
		return complex_sub(left,righ)
	elif expr_dict[expr_head]['opr'] == '*' :
		return complex_multiply(left,righ)
	elif expr_dict[expr_head]['opr'] == '/' :
		return complex_division(left,righ)

	return ['','']
# end def complex_expr()

def complex_add(left,righ):
	return [left[0]+'+'+righ[0], \
		      left[1]+'+'+righ[1]]

def complex_sub(left,righ):
	return [left[0]+'-'+righ[0], \
		      left[1]+'-'+righ[1]]

def complex_multiply(left,righ):
	return [left[0]+'*'+righ[0]+'-'+left[1]+'*'+righ[1], \
		      left[0]+'*'+righ[1]+'+'+left[1]+'*'+righ[0]]

def complex_division(left,righ):
	return ['('+left[0]+'*'+righ[0]+'+'+left[1]+'*'+righ[1]+')/('+righ[0]+'*'+righ[0]+'+'+righ[1]+'*'+righ[1]+')', \
		  	 '(-'+left[0]+'*'+righ[1]+'+'+left[1]+'*'+righ[0]+')/('+righ[0]+'*'+righ[0]+'+'+righ[1]+'*'+righ[1]+')']

def complex_expr_trans(expr):
	
	cplx_list = []
	if expr.find('_') != -1:
		return ['','']
	expr = expr.replace(' ','')
	expr_dict = {}
	expr_list = expr2list(expr)

	expr_order = parsing_with_bracket_opr(expr_list,expr_dict,[['*','/'],['+','-']],0)
	trans_complex_expr_list(expr_dict)

	return complex_expr('expr_'+str(expr_order),expr_dict)
#	end complex_expr_trans()