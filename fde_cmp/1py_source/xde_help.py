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
keyfunc['ARRAY']  = ''
keyfunc['COEF']   = "Declare the component of couple varaible as 'COEF un vn wn', where 'un vn wn' may be last time or iterate step resault of its field."
keyfunc['COOR']   = "Declare the component of axis as 'COOR x y z'."
keyfunc['COMMON'] = ''
keyfunc['DAMP']   = ''
keyfunc['DEFI']   = ''
keyfunc['DISP']   = "Declare the component of field as 'DISP u v w'."
keyfunc['DIST']   = ''
keyfunc['END']    = ''
keyfunc['FUNC']   = ''
keyfunc['FVECT']  = ''
keyfunc['FMATR']  = ''
keyfunc['GAUS']   = ''
keyfunc['LOAD']   = ''
keyfunc['MATE']   = ''
keyfunc['MASS']   = ''
keyfunc['MATRIX'] = ''
keyfunc['SHAP']   = "Declare shap functions.... to be imporve"
keyfunc['STIF']   = ''
keyfunc['VECT']   = "Declare a vector form as 'VECT a a1 a2 a3' or 'VECT a=a1 a2 a3' means 'a=(a1,a2,a3)'."
keyfunc['USER']   = ''
keyfunc['$CC']    = "Use '$cc' as '$cc double aa;', insert a line of C code."
keyfunc['$C6']    = ''
keyfunc['$CV']    = "Use '$cv' as '$cv a_i = c_i_j*d_j' or '$cv a = {u/x}', to make tensor calculation or make derivative of couple varaible."
keyfunc['$CP']    = ''
keyfunc['$I']     = ''
keyfunc['@L']     = "Use '@L' as '@L grad.xyz f fe x y z u' to calculate gradian of u...... "
keyfunc['@A']     = ''
keyfunc['@W']     = ''
keyfunc['@S']     = ''
keyfunc['@R']     = ''
    
import re as regx
def xde_help(input_key):

    # gather the similar keys in keywords
    gather_key, key_find = [], 0

    if input_key[0] == '$': input_key = '\\'+input_key

    for xde_key in keywords:
        
        regx_ex = regx.match(input_key, xde_key, regx.I)
        if regx_ex != None:
            regx_ex = regx_ex.group()

            if input_key[0] == '\\': 
                input_key = input_key[1:len(input_key)]

            if input_key.upper() == xde_key:
                key_find = 1
            else: gather_key.append(xde_key)

    # if hit the xde_key, show the corresponding help information
    # else show all the similar keys
    if key_find == 1:
        if xde_key.upper() in keywords:
            print(keyfunc[xde_key.upper()])
    elif input_key.lower() == 'all':
        for keys in keyfunc:
            auto_line_break_print(maxl)
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
        if   quot_find == 0 and char == '\'':
            quot_find = 1
        elif quot_find == 1 and char == '\'':
            quot_find = 0
            quot_strs += char
            quot_strs_list.append(quot_strs)
            quot_strs = ''
        if quot_find == 1:
            quot_strs += char

    for strr in quot_strs_list:
        chars = chars.replace(strr, strr.replace(' ','\n'))

    words_list = chars.split(' ')
    for i, strr in enumerate(words_list):
        words_list[i] = strr.replace('\n', ' ')
    return words_list

def auto_line_break_print(maxl):
    output = keys + ' '*(6-len(keys)) + ' : '
    output_list = []
    help_info_list = split_sentense(keyfunc[keys])

    while True:
        temp_str = ' '*8
        for i, strr in enumerate(help_info_list):
            temp_str += f' {strr}'
            if len(temp_str) > maxl:
                temp_str = temp_str.replace(f' {strr}','')
                help_info_list = help_info_list[i:]
                output_list.append(temp_str)
                break

        if len(temp_str) == len(' '*9+' '.join(help_info_list)):
            output_list.append(temp_str+'\n')
            break

    for i, strr in enumerate(output_list):
        if i == 0: print(strr.replace(' '*9, output))
        else:print(strr)
