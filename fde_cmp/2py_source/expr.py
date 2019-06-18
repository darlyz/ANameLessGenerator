'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-19
 Author: Zhang_Licheng
 Title: complex, tensor expression in dummy index summation
 All rights reserved
'''
import re as regx
# ------------------------------------------------------------------------------
# --------------------------------base expr class-------------------------------
# ------------------------------------------------------------------------------
class expr:
    expr_strs, expr_list, expr_dict, expr_head = '', [], {}, ''
    def __init__(self,strs, opr_oder_list=[['*','/'],['+','-']]):
        self.expr_strs = strs
        opr_list = [x for y in opr_oder_list for x in y] + ['(',')']
        self.expr_list = expr_strs2list(self.expr_strs, opr_list)
        self.expr_ordr = parsing_with_bracket_opr(self.expr_list.copy(), self.expr_dict, opr_oder_list, 0)
        self.expr_head = 'expr_'+str(self.expr_ordr)
    def show_expr_strs(self):
        return self.expr_strs
    def show_expr_list(self):
        return self.expr_list
    def show_expr_dict(self):
        return self.expr_dict

    def bracket_expand(self, expr_head):

        for strs in ['left','righ'] :
            if self.expr_dict[expr_head][strs].find('expr') != -1:

                expr_sub = self.expr_dict[expr_head][strs]
                self.expr_dict[expr_head][strs] = self.bracket_expand(expr_sub)

        left = self.expr_dict[expr_head]['left']
        righ = self.expr_dict[expr_head]['righ']
        opr  = self.expr_dict[expr_head]['opr']

        left_list = split_unequal_grade_expr(left)
        righ_list = split_unequal_grade_expr(righ)

        expr_strs = ''

        if opr == '*':
            for left_str in left_list:
                for righ_str in righ_list:
                    left_opr, righ_opr = left_str[0], righ_str[0]
                    left_val, righ_val = left_str.lstrip(left_opr), righ_str.lstrip(righ_opr)
                    if   left_opr == righ_opr: strs_opr = '+'
                    elif left_opr != righ_opr: strs_opr = '-'
                    expr_strs += strs_opr + left_val + '*' + righ_val
        elif opr == '/':
            for left_str in left_list:
                if len(righ_list) != 1 or righ[0] == '-':
                    righ = '(' + righ + ')'
                expr_strs += left_str + '/' + righ
        elif opr == '-':
            expr_strs += left
            for righ_str in righ_list:
                righ_opr = righ_str[0]
                righ_val = righ_str.lstrip(righ_opr)
                if   righ_opr == '-': strs_opr = '+'
                elif righ_opr == '+': strs_opr = '-'
                expr_strs += strs_opr + righ_val
        elif opr == '+':
            expr_strs += left + (righ if righ[0] in ['-','+'] else '+'+righ)

        return expr_strs

# -a+b*c --> ['-a','+b*c']
def split_unequal_grade_expr(expr_strs):
    opr_list = regx.findall(r'\+|\-',expr_strs)
    val_list = regx.split(r'\+|\-',expr_strs)

    if val_list[0] == '':
        val_list.pop(0)
    else:
        opr_list.insert(0,'+')

    return [opr+val for opr,val in zip(opr_list,val_list)]

#   (-a+b)*c --> ['(','-a','+','b',')','*','c']
def expr_strs2list (expr_strs,opr_list=['+','-','*','/','(',')']): 
    
    # make it compact
    expr_strs = expr_strs.replace(' ','')
    
    # transform self-sign: 
    # +a --> a; -a --> neg_a; (a) --> a
    if expr_strs[0] == '+':
        expr_strs = expr_strs.lstrip('+')
    elif expr_strs[0] == '-':
        expr_strs = 'neg_'+expr_strs.lstrip('-')
    expr_strs = expr_strs.replace('(+','(').replace('(-','(neg_')
    single_val = regx.findall(r'\([a-z]\w*\)', expr_strs, regx.I)
    for val in single_val:
        expr_strs = expr_strs.replace(val, val.lstrip('(').rstrip(')'))

    # split
    val_start, val_end, expr_list = 0, 0, []
    for ii,char in enumerate(expr_strs) :
        if char in opr_list:
            if val_start != val_end:
                expr_list.append(expr_strs[val_start:val_end].replace('neg_','-'))
            expr_list.append(char)
            val_start = ii + 1
        val_end = ii+1
        
    if val_start != len(expr_strs):
        expr_list.append(expr_strs[val_start:len(expr_strs)])

    return expr_list
# end expr2list()

# ['a','*','b','/','c'] -->         expr2:'/'   --> return head order: 2
#  'a*b/c'                         /     \
#                             expr1:'*'   c
#                            /     \
#                           a       b
def parsing_equal_grade_opr(expr_list, expr_dict, opr_list, expr_order):

    expr_i = expr_order
    expr_name = ''

    for i, strs in enumerate(expr_list):

        if strs in opr_list:

            expr_i += 1
            expr_name = 'expr_'+str(expr_i)
            expr_dict[expr_name] = {}
            expr_dict[expr_name]['opr']  = strs

            if i > 2:
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

    all_opr = set([opr for opr_list in opr_lists for opr in opr_list])

    for opr_list in opr_lists[:-1]:
        all_opr = all_opr.difference(set(opr_list))
        upper_expr_lists, upper_expr_locat, upper_start, upper_end, upper_find = [], [], 0, 0, 0

        # draw the upper grade operator expression
        for list_i, strs in enumerate(expr_list):

            if strs in opr_list:
                if upper_find == 0:
                    upper_start = list_i - 1
                    upper_find = 1

            elif strs in all_opr or list_i == len(expr_list) - 1:
                if upper_find == 1:
                    if strs in all_opr:
                        upper_end = list_i
                    elif list_i == len(expr_list) - 1:
                        upper_end = list_i + 1
                    upper_find = 0

            if upper_start != 0 and upper_end != 0:
                upper_expr_lists.append(expr_list[upper_start:upper_end])
                upper_expr_locat.append(list(range(upper_start,upper_end)))
                upper_start, upper_end = 0, 0

        # parsing the upper grade operator expression and replace them in expr_list
        for list_i, upper_list in enumerate(upper_expr_lists):

            # parsing
            expr_i = parsing_equal_grade_opr(upper_list, expr_dict, opr_list, expr_i)

            # replacing
            upper_locat = upper_expr_locat[list_i]
            for locat_i, upper in enumerate(upper_locat):
                if locat_i == 0:
                    expr_list[upper] = 'expr_'+str(expr_i)
                else:
                    expr_list[upper] = ''

        # replacing
        expr_list = [strs for strs in expr_list if strs != '']

    expr_i = parsing_equal_grade_opr(expr_list, expr_dict, all_opr, expr_i)
    
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
    max_bracket_level = 0
    for strs in expr_list:
        if   strs == '(': bracket_tag += 1
        elif strs == ')': bracket_tag -= 1

        if  max_bracket_level < bracket_tag:
            max_bracket_level = bracket_tag

    for level in reversed(range(1,max_bracket_level+1)):

        # locate the bracket
        bracket_tag = 0
        left_bracket_locat, righ_bracket_locat = [], []
        for list_i, strs in enumerate(expr_list):

            if   strs == '(':
                bracket_tag += 1
                if bracket_tag == level:
                    left_bracket_locat.append(list_i)

            elif strs == ')':
                if bracket_tag == level:
                    righ_bracket_locat.append(list_i)
                bracket_tag -= 1

        # draw expression in bracket, parsing and replace them
        bracket_i = 0
        for left_locat, righ_locat in zip(left_bracket_locat, righ_bracket_locat):
            bracket_expr = expr_list[left_locat+1:righ_locat]

            # parsing bracket expression
            expr_i = parsing_unequal_grade_opr(bracket_expr, expr_dict, opr_lists, expr_i)

            # replace the bracket expression in expr_list
            for kk in range(left_locat, righ_locat+1):
                expr_list[kk] = 'expr_'+str(expr_i) if kk == left_locat else ''

            bracket_i += 1

        # replace the bracket expression in expr_list
        expr_list = [strs for strs in expr_list if strs != '']

    expr_i = parsing_unequal_grade_opr(expr_list, expr_dict, opr_lists, expr_i)

    return expr_i
# end parsing_with_bracket_opr()

# ------------------------------------------------------------------------------
# ----------------------------complex expr class--------------------------------
# ------------------------------------------------------------------------------
class cmplx_expr(expr):
    complex_list = []
    def __init__(self,strs,opr_oder_list=[['*','/'],['+','-']]):
        expr.__init__(self,strs,opr_oder_list=[['*','/'],['+','-']])
        self.trans_complex_expr_list()
        self.complex_list = self.complex_expand(self.expr_head)

    # transform 'a' to ['ar','ai'] in expr_dict
    def trans_complex_expr_list(self):
        for keys in self.expr_dict.keys():
            for side in ['left','righ']:
                if  isinstance(self.expr_dict[keys][side],str) == 1 \
                and self.expr_dict[keys][side].find('expr') == -1 \
                and self.expr_dict[keys][side] != '0':
                    var = self.expr_dict[keys][side]
                    self.expr_dict[keys][side] = [var+'r',var+'i']
    # end trans_complex_expr_list()

    # expand complex expression
    def complex_expand(self,expr_head):

        expr_sub = ''

        for strs in ['left','righ']:
            if not isinstance(self.expr_dict[expr_head][strs],list) \
            and self.expr_dict[expr_head][strs].find('expr') != -1:

                expr_sub = self.expr_dict[expr_head][strs]
                self.expr_dict[expr_head][strs] = self.complex_expand(expr_sub)

                if  self.expr_dict[expr_head]['opr'] in ['*','/'] \
                and self.expr_dict[expr_sub ]['opr'] in ['+','-','*'] :
                    self.expr_dict[expr_head][strs] = complex_add_bracket(self.expr_dict[expr_head][strs])

        left = self.expr_dict[expr_head]['left']
        righ = self.expr_dict[expr_head]['righ']

        if self.expr_dict[expr_head]['opr'] == '+' :
            return complex_add(left,righ)
        elif self.expr_dict[expr_head]['opr'] == '-' :
            return complex_sub(left,righ)
        elif self.expr_dict[expr_head]['opr'] == '*' :
            return complex_multiply(left,righ)
        elif self.expr_dict[expr_head]['opr'] == '/' :
            return complex_division(left,righ)

        return ['','']
    # end def complex_expand()

def complex_add(left,righ):
    if left == '0' and righ != '0':
        return righ
    elif righ == '0' and left != '0':
        return left
    elif righ != '0' and left != '0':
        return [left[0]+'+'+righ[0], left[1]+'+'+righ[1]]
    else: return '0'

def complex_sub(left,righ):
    if left == '0' and righ != '0':
        return ['-'+righ[0],'-'+righ[1]]
    elif righ == '0' and left != '0':
        return left
    elif righ != '0' and left != '0':
        return [left[0]+'-'+righ[0], left[1]+'-'+righ[1]]
    else: return '0'

def complex_multiply(left,righ):
    if righ != '0' and left != '0':
        return [left[0]+'*'+righ[0]+'-'+left[1]+'*'+righ[1], \
                left[0]+'*'+righ[1]+'+'+left[1]+'*'+righ[0]]
    else: return '0'

def complex_division(left,righ):
    if righ != '0' and left != '0':
        return ['(' +left[0]+'*'+righ[0]+'+'+left[1]+'*'+righ[1]+')/('+righ[0]+'*'+righ[0]+'+'+righ[1]+'*'+righ[1]+')', \
                '(-'+left[0]+'*'+righ[1]+'+'+left[1]+'*'+righ[0]+')/('+righ[0]+'*'+righ[0]+'+'+righ[1]+'*'+righ[1]+')']
    elif left == '0' and righ != '0':
        return '0'
    else: return None

def complex_add_bracket(complex_list):
    temp_list = []
    for strs in complex_list:
        temp_list.append('('+strs+')')
    return temp_list
# end vector_add_bracket()

# ------------------------------------------------------------------------------
# -----------------------------tensor expr class--------------------------------
# ------------------------------------------------------------------------------
class tnsr_expr(expr): # need to release
    tnsr_list = []

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
# [a21,a22]      [b12,b22]       [a21*b11+a22*b21, a21*b12+a22*b22]
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
        matrix_list = matrix_multiply(expr_dict[expr_head]['left'], \
                                      expr_dict[expr_head]['righ'])
    else:
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

# ------------------------------------------------------------------------------
# --------------------------dummy index expr summation--------------------------
# ------------------------------------------------------------------------------
def idx_summation(left_var,righ_expr,xde_lists):
    tensor_dict = {}
    for keys in ['vect','fvect']:
        if keys in xde_lists:
            for strs, lists in xde_lists[keys].items():
                tlist = lists[1:len(lists)]
                for ii in range(len(tlist)):
                    tlist[ii] = tlist[ii].lstrip('+')
                    if len(split_bracket_expr(tlist[ii])) != 1 :
                        tlist[ii] = '('+tlist[ii]+')'
                    tensor_dict[strs+str(ii)] = tlist[ii]
    for keys in ['matrix','fmatr']:
        if keys in xde_lists:
            for strs, lists in xde_lists[keys].items():
                tlist = lists[2:len(lists)]
                for ii in range(len(tlist)):
                    for jj in range(len(tlist[ii])):
                        tlist[ii][jj] = tlist[ii][jj].lstrip('+')
                        if len(split_bracket_expr(tlist[ii][jj])) != 1 :
                            tlist[ii][jj] = '('+tlist[ii][jj]+')'
                        tensor_dict[strs+str(ii)+str(jj)] = tlist[ii][jj]

    left_var_list = []
    left_idxlen = {}
    #left_indxs  = parse_xde_type_tensor(left_var,left_var_list,left_idxlen,xde_lists)
    # -- copy parse_xde_type_tensor()
    left_var_list = left_var.split('_')
    if ('vect'   in xde_lists and left_var_list[0] in xde_lists['vect']) \
    or ('matrix' in xde_lists and left_var_list[0] in xde_lists['matrix']) :
        if   len(left_var_list) == 2:
            left_idxlen[left_var_list[1]] = int(xde_lists['vect'][left_var_list[0]][0])

        elif len(left_var_list) == 3:
            left_idxlen[left_var_list[1]] = int(xde_lists['matrix'][left_var_list[0]][0])
            left_idxlen[left_var_list[2]] = int(xde_lists['matrix'][left_var_list[0]][1])

    elif ('fvect' in xde_lists and left_var_list[0] in xde_lists['fvect']) \
    or   ('fmatr' in xde_lists and left_var_list[0] in xde_lists['fmatr']) :
        if   len(left_var_list) == 2:
            left_idxlen[left_var_list[1]] = int(xde_lists['fvect'][left_var_list[0]][0])

        elif len(left_var_list) == 3:
            left_idxlen[left_var_list[1]] = int(xde_lists['fmatr'][left_var_list[0]][0])
            left_idxlen[left_var_list[2]] = int(xde_lists['fmatr'][left_var_list[0]][1])

    else: pass
        
    left_indxs = list(left_idxlen.keys())
    # -- copy parse_xde_type_tensor()

    left_indxi = {}
    for keys in left_idxlen.keys():
        left_indxi[keys] = 0

    righ_pack = {'righ_exp':[],'righ_len':[],'righ_rdx':[],'righ_idx':[]}
    righ_expr_list = split_bracket_expr(righ_expr)
    righ_pack['righ_exp'] = righ_expr_list

    for expr_strs in righ_expr_list:

        # find tensors in right expression
        righ_idxlen = {}
        righ_indxs  = []
        pattern = regx.compile(r'[\^a-zA-Z]+(?:_[a-zA-Z])+')
        tensor_list = pattern.findall(expr_strs)

        # find indexs in right expression and pop non-repetitive tensors and indexs
        temp_list  = []
        for strs in tensor_list:

            if temp_list.count(strs) == 0:
                temp_list.append(strs)

            temp_idxsl = strs.split('_')

            if ('vect'   in xde_lists and temp_idxsl[0] in xde_lists['vect']) \
            or ('matrix' in xde_lists and temp_idxsl[0] in xde_lists['matrix']) :

                if   len(temp_idxsl) == 2:
                    if not temp_idxsl[1] in left_idxlen:
                        righ_idxlen[temp_idxsl[1]] = int(xde_lists['vect'][temp_idxsl[0]][0])

                elif len(temp_idxsl) == 3:
                    if not temp_idxsl[1] in left_idxlen:
                        righ_idxlen[temp_idxsl[1]] = int(xde_lists['matrix'][temp_idxsl[0]][0])
                    if not temp_idxsl[2] in left_idxlen:
                        righ_idxlen[temp_idxsl[2]] = int(xde_lists['matrix'][temp_idxsl[0]][1])

            elif ('fvect' in xde_lists and temp_idxsl[0] in xde_lists['fvect']) \
            or   ('fmatr' in xde_lists and temp_idxsl[0] in xde_lists['fmatr']) :

                if   len(temp_idxsl) == 2:
                    if not temp_idxsl[1] in left_idxlen:
                        righ_idxlen[temp_idxsl[1]] = int(xde_lists['fvect'][temp_idxsl[0]][0])

                elif len(temp_idxsl) == 3:
                    if not temp_idxsl[1] in left_idxlen:
                        righ_idxlen[temp_idxsl[1]] = int(xde_lists['fmatr'][temp_idxsl[0]][0])
                    if not temp_idxsl[2] in left_idxlen:
                        righ_idxlen[temp_idxsl[2]] = int(xde_lists['fmatr'][temp_idxsl[0]][1])

            else: pass

        tensor_list = temp_list.copy()
        righ_indxs = list(righ_idxlen.keys())
        righ_indxi = {}
        for keys in righ_idxlen.keys():
            righ_indxi[keys] = 0

        righ_pack['righ_len'].append(righ_idxlen)
        righ_pack['righ_rdx'].append(righ_indxi)
        righ_pack['righ_idx'].append(righ_indxs)

    expr_list = []
    left_loop(0, left_var, righ_pack, tensor_dict, \
              left_indxs, left_indxi, left_idxlen, \
                  expr_list)

    return expr_list
#end idx_summation()

# xde_tnsr --> xde_tnsr_list & tnsr_dict   return->
# a_i_j    --> [a,i,j]         {i:2,j:3}   [i,j]
def parse_xde_type_tensor(xde_tnsr,xde_tnsr_list,tnsr_dict,xde_lists):

    if xde_tnsr.find('_') == -1:
        return []
    else:
        for strs in xde_tnsr.split('_'):
            xde_tnsr_list.append(strs)
        if ('vect'   in xde_lists and xde_tnsr_list[0] in xde_lists['vect']) \
        or ('matrix' in xde_lists and xde_tnsr_list[0] in xde_lists['matrix']) :
            if   len(xde_tnsr_list) == 2:
                tnsr_dict[xde_tnsr_list[1]] = int(xde_lists['vect'][xde_tnsr_list[0]][0])

            elif len(xde_tnsr_list) == 3:
                tnsr_dict[xde_tnsr_list[1]] = int(xde_lists['matrix'][xde_tnsr_list[0]][0])
                tnsr_dict[xde_tnsr_list[2]] = int(xde_lists['matrix'][xde_tnsr_list[0]][1])

        elif ('fvect' in xde_lists and xde_tnsr_list[0] in xde_lists['fvect']) \
        or   ('fmatr' in xde_lists and xde_tnsr_list[0] in xde_lists['fmatr']) :
            if   len(xde_tnsr_list) == 2:
                tnsr_dict[xde_tnsr_list[1]] = int(xde_lists['fvect'][xde_tnsr_list[0]][0])

            elif len(xde_tnsr_list) == 3:
                tnsr_dict[xde_tnsr_list[1]] = int(xde_lists['fmatr'][xde_tnsr_list[0]][0])
                tnsr_dict[xde_tnsr_list[2]] = int(xde_lists['fmatr'][xde_tnsr_list[0]][1])

        else: pass

    return list(tnsr_dict.keys())
# end parse_xde_type_tensor()

# loop the right tensor of expression by the lowest short expression
# which are the sub-loop of left tensor
def righ_loop(loop_level=0, expr_item='', tensor_dict={}, \
              loop_idx=[], loop_rdx={}, loop_len={}, fixd_idx={}, \
                    expr_sum_list=[]):
    #global righ_loop_count
    expr = expr_item
    if(loop_level == len(loop_idx)):
        #righ_loop_count += 1
        for keys,vals in loop_rdx.items():
            expr = expr.replace('_'+keys,str(vals))
        for keys,vals in fixd_idx.items():
            expr = expr.replace('_'+keys,str(vals))

        var_list = regx.split  (r'\+|\-|\*|\/|\(|\)|\[|\]|\;',expr)
        opr_list = regx.findall(r'\+|\-|\*|\/|\(|\)|\[|\]|\;',expr)
        var1_list = []
        for strs in var_list:
            if strs!='' and strs in tensor_dict.keys():
                var1_list.append(strs.replace(strs,tensor_dict[strs]))
            else:
                var1_list.append(strs)
        expr = ''
        for ii in range(len(opr_list)):
            expr += var1_list[ii]
            expr += opr_list[ii]
        expr += var1_list[len(opr_list)]

        expr_sum_list.append(expr)
        return
    for ii in range(loop_len[loop_idx[loop_level]]):
        loop_rdx[loop_idx[loop_level]] = ii
        righ_loop(loop_level+1, expr_item, tensor_dict, \
                  loop_idx, loop_rdx, loop_len, fixd_idx, \
                      expr_sum_list)
#end righ_loop()

# loop the left tensor of expression
def left_loop(loop_level=0, left_var='', righ_pack={}, tensor_dict={}, \
              loop_idx=[], loop_rdx={}, loop_len={}, \
              expr_list=[]):
    #global left_loop_count
    if left_var.find('_') != -1:
        var = left_var
        if loop_level == len(loop_idx):
            #left_loop_count += 1
            for keys,vals in loop_rdx.items():
                var = var.replace('_'+keys,str(vals))
            var = var.replace(var,tensor_dict[var])
            var += '='
            i = 0
            for expr_item in righ_pack['righ_exp']:
                expr_sum_list = []
                righ_loop(0, expr_item, tensor_dict, \
                          righ_pack['righ_idx'][i], righ_pack['righ_rdx'][i], righ_pack['righ_len'][i], loop_rdx, \
                              expr_sum_list)
                i += 1
                for strs in expr_sum_list:
                    var += strs
            expr_list.append(var)
            return
        for ii in range(loop_len[loop_idx[loop_level]]):
            loop_rdx[loop_idx[loop_level]] = ii
            left_loop(loop_level+1, left_var, righ_pack, tensor_dict, \
                      loop_idx, loop_rdx, loop_len, \
                        expr_list)
    else:
        var = left_var
        var += '='
        i = 0
        for expr_item in righ_pack['righ_exp']:
            expr_sum_list = []
            righ_loop(0, expr_item, tensor_dict, \
                      righ_pack['righ_idx'][i], righ_pack['righ_rdx'][i], righ_pack['righ_len'][i], loop_rdx, \
                          expr_sum_list)
            i += 1
            for strs in expr_sum_list:
                var += strs
        expr_list.append(var)
        return
#end left_loop()


# split expr to list by the lowest priority
def split_bracket_expr(expr):
    expr_list = []
    bracket_count  = 0
    expr_left_addr = 0
    expr_righ_addr = 0
    for ii in range(len(expr)):
        if expr[ii] == '(':
            bracket_count += 1
        elif expr[ii] == ')':
            bracket_count -= 1

        if ((expr[ii] == '+' \
        or   expr[ii] == '-') \
        and bracket_count == 0) \
        or ii == len(expr)-1:
            if ii == len(expr)-1:
                expr_righ_addr = ii+1
            else:
                expr_righ_addr = ii
            expr_list.append(expr[expr_left_addr:expr_righ_addr].replace(' ',''))
            expr_left_addr = expr_righ_addr

    return [strs for strs in expr_list if strs != '']
# end split_bracket_expr()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------