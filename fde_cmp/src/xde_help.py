'''
 Copyright: Copyright (c) 2019
 Created: 2019-6-19
 Author: Zhang_Licheng
 Title: help system for xde
 All rights reserved
'''

keywords  = ['ARRAY','COEF','COOR','COMMON','DAMP','DEFI','DISP','DIST','END'] \
          + ['FUNC','FVECT','FMATR','GAUS','LOAD','MATE','MASS','MATRIX','SHAP','STIF','VECT'] \
          + ['USER','$CC','$C6','$CV','$CP','$I','@L','@A','@W','@S','@R']

keyfunc = {}
keyfunc['ARRAY']  = "Declare tensor variables, '*[d]' means vector, '^*[d][d]' means matrix. " \
                  + "For instance, 'ARRAY a[3],^b[2][3]', note that '^' at head of matrix."

keyfunc['COEF']   = "Declare the component of couple varaible as 'COEF un vn wn', " \
                  + "where 'un vn wn' may be last time or iterate step resault of its field."

keyfunc['COOR']   = "Declare the component of axis as 'COOR x y z'."

keyfunc['COMMON'] = "Declare the global variable. For example, 'COMMON double aa'."

keyfunc['DAMP']   = "Declare the damping items of weak form, " \
                  + "if it is lumped, write a line as 'DAMP %1 var1*var2', " \
                  + "or if it is distributed, write a paragraph as following:\n" \
                  + '\t'*2 + "DAMP\n" \
                  + '\t'*2 + "DIST=+[u;u]*var1..."

keyfunc['DEFI']   = "Declare the beginning of xde script, if 'MATE' line at the first paragraph, it could be omitted."

keyfunc['DISP']   = "Declare the component of field as 'DISP u v w'."

keyfunc['DIST']   = "Declare distributed weak items. use as 'DIST=+[u;u]*var1...'."

keyfunc['END']    = 'Declare the end of xde script, it could be omitted.'

keyfunc['FUNC']   = "If it write as a line, it declare the derivative variable of 'disp', " \
                  + "write as 'FUNC ux uy uz', and 'ux uy uz' could be gradian of u. " \
                  + "And if it write as a paragraph, it lead the following lines to give " \
                  + "expressions of derivative variable, for example 'ux = +[u/x]'."

keyfunc['FVECT']  = "Declare a F vector to contain the result form of operator, as 'FVECT Fv 3'."

keyfunc['FMATR']  = "Declare a F matrix to contain the result form of operator, as 'FMATR Fm 3 2'."

keyfunc['GAUS']   = "Declare the gaussian integral type, write as 'GAUS %3' determined by mdi file, or write as 'GAUS 2' means order 2"

keyfunc['LOAD']   = "Declare the load items. If it writed as a line 'LOAD fx fy fz', " \
                  + "the variables following 'LOAD' must compare to the number of 'DISP' declared." \
                  + " Or it writed as a paragraph as 'LOAD=[u]*fx+[v]*fy...'."

keyfunc['MATE']   = "Declare the material variables and their values, " \
                  + "variables suggested to be ahead of values and it is better numerical equal."

keyfunc['MASS']   = "Declare the mass items of weak form, " \
                  + "if it is lumped, write a line as 'MASS %1 var1*var2', " \
                  + "or if it is distributed, write a paragraph as following:\n" \
                  + '\t'*2 + "MASS\n" \
                  + '\t'*2 + "DIST=+[u;u]*var1..."

keyfunc['MATRIX'] = 'Write as a paragraph to declare a matrix:\n' \
                  + '\t'*2 + 'matrix m 2 2\n' \
                  + '\t'*2 + 'm11 m12\n' \
                  + '\t'*2 + 'm21 m22'

keyfunc['SHAP']   = "Declare shap functions as 'SHAP %1 %2' determined by mdi file."

keyfunc['STIF']   = "Declare the stiffness items of weak form, " \
                  + "it is distributed, write a paragraph as following:\n" \
                  + '\t'*2 + "STIF\n" \
                  + '\t'*2 + "DIST=+[u;u]*var1..."

keyfunc['VECT']   = "Declare a vector form as 'VECT a a1 a2 a3' or 'VECT a=a1 a2 a3' means 'a=(a1,a2,a3)'."

keyfunc['USER']   = 'Declare a paragraph that insert multiline of code at the end of code script.'

keyfunc['$CC']    = "Use '$cc' as '$cc double aa;', insert a line of C code."

keyfunc['$C6']    = "Use '$c6' as '$c6 double aa;', insert a line of C code."

keyfunc['$CV']    = "Use '$cv' as '$cv a_i = c_i_j*d_j' or '$cv a = {u/x}', " \
                  + "to make tensor calculation or make derivative of couple varaible."

keyfunc['$CP']    = "Use '$cp' as '$cp a=b*c' to make complex calculation, " \
                  + "if it has tensor form as '$cp a = b_i*c_i', make tensor calculation first."

keyfunc['$I']     = 'Insert the following code at the initial place.'

keyfunc['@L']     = "Use '@L' to make operator calculation, for example '@L grad.xyz f fe x y z u' "\
                  + "to calculate gradian of u, and assign the form of gradian to fe."

keyfunc['@A']     = "Use '@A' as '@A fv=+[fvv_i]*m_i_j+[fm_i_j]*1' " \
                  + "where 'fv,fvv' is f vector, 'fm' is f matrix, and 'm' is matrix."

keyfunc['@W']     = "Use '@W' as '@W v fv 1 5 9...', where 'v' is vector or matrix, " \
                  + "'fv' is f vector or f matrix, and '1 5 9...' is the index of 'fv', " \
                  + "and the components number of 'v' must be compare to length of '1 5 9...'. "\
                  + "The following digitals '1 5 9...' could be omitted, then " \
                  + "and the components number of 'v' must be compare to length of 'fv'."

keyfunc['@S']     = "Use '@S' as '@S fe fv 1 5 9...', " \
                  + "'fe' and 'fv' are f vector or f matrix, and '1 5 9...' is the index of 'fv', " \
                  + "and the components number of 'v' must be compare to length of '1 5 9...'. "\
                  + "The following digitals '1 5 9...' could be omitted, then " \
                  + "and the components number of 'fe' must be compare to length of 'fv'."

keyfunc['@R']     = "Use '@R' as '@R fv_i=+[u_i]*m_i_j+[gradu_j]*1' " \
                  + "where 'fv' is f vector, 'u' is f matrix of 'disp', and 'm' is matrix." \
                  + "'gradu' is vector of 'func'."

import re

def xde_help(input_key):

    # gather the similar keys in keywords
    gather_key, key_find = [], 0

    if input_key[0] == '$':
        input_key = f'\\{input_key}'

    for xde_key in keywords:
        
        if re.match(input_key, xde_key, re.I) != None:
            
            if input_key[0] == '\\':
                finded_key = input_key[1:]

            else: 
                finded_key = input_key

            if finded_key.upper() == xde_key:
                key_find = 1
                break

            else: 
                gather_key.append(xde_key)

    # if hit the xde_key, show the corresponding help information
    # else show all the similar keys
    from os import get_terminal_size
    maxcol = get_terminal_size().columns - 10

    if key_find == 1:
        auto_line_break_print(maxcol, 6, finded_key.upper(), keyfunc[finded_key.upper()])

    elif input_key.lower() == 'all':
        for keys in keyfunc:
            auto_line_break_print(maxcol, 6, keys, keyfunc[keys])

    else:

        if len(gather_key) != 0:
            print("do you find '{}'?".format("','".join(gather_key)))

        else:
            print(f"xde keys: {keywords}.")

def split_sentense(chars):

    quot_find = 0
    quot_strs = ''
    quot_strs_list = []

    for char in chars:

        if   quot_find == 0 \
        and char == '\'':
            quot_find = 1

        elif quot_find == 1 \
        and char == '\'':
            quot_find = 0
            quot_strs += char
            quot_strs_list.append(quot_strs)
            quot_strs = ''

        if quot_find == 1:
            quot_strs += char

    for strr in quot_strs_list:
        chars = chars.replace(strr, strr.replace(' ','\a'))

    words_list = chars.split(' ')

    for i, strr in enumerate(words_list):
        words_list[i] = strr.replace('\a', ' ')

    return words_list

def auto_line_break_print(line_len, key_len, keys, sentense):

    output = keys + ' '*(key_len-len(keys)) + ' : '
    output_list = []
    help_info_list = split_sentense(sentense)

    while True:
        temp_str = ' '*(key_len+2)

        for i, strr in enumerate(help_info_list):
            temp_str += f' {strr}'

            if len(temp_str) > line_len:
                temp_str = temp_str.replace(f' {strr}','')
                help_info_list = help_info_list[i:]
                output_list.append(temp_str)
                break

        if len(temp_str) == len(' '*(key_len+3)+' '.join(help_info_list)):
            output_list.append(temp_str+'\n')
            break

    for i, strr in enumerate(output_list):

        if i == 0:
            print(strr.replace(' '*(key_len+3), output))
            
        else:
            print(strr)
