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
        show_help(input_key)
    else:
        if len(gather_key) != 0:
            print("do you find '{}'?".format("','".join(gather_key)))
        else:
            print(f"xde keys: {keywords}.")


def show_help(xde_key):
    if xde_key.lower() == '$cc':
        print("Use '$cc' as '$cc double aa;', insert a line of C code.")

    elif xde_key.lower() == '$cv':
        print("Use '$cv' as '$cv a_i = c_i_j*d_j' or '$cv a = {u/x}', to make tensor calculation or make derivative of couple varaible.")

    elif xde_key.lower() == '$cp':
        print("Use '$cp' as '$cp a = b + c' means make complex calculation as 'ar = br + cr' and 'ai = bi + ci'. And it could make tensor calculation first.")

    elif xde_key.lower() == '@l':
        print("Use '@L' as '@L grad.xyz f fe x y z u' to calculate gradian of u...... ")

    elif xde_key.lower() == 'disp':
        print("Declare the component of field as 'DISP u v w'.")

    elif xde_key.lower() == 'coor':
        print("Declare the component of axis as 'COOR x y z'.")

    elif xde_key.lower() == 'coef':
        print("Declare the component of couple varaible as 'COEF un vn wn', where 'un vn wn' may be last time or iterate step resault of its field.")

    elif xde_key.lower() == 'func': pass

    elif xde_key.lower() == 'vect':
        print("Declare a vector form as 'VECT a a1 a2 a3' or 'VECT a=a1 a2 a3' means 'a=(a1,a2,a3).")

    elif xde_key.lower() == 'matrix': pass

    elif xde_key.lower() == 'fvect': pass

    elif xde_key.lower() == 'fmatr': pass

    elif xde_key.lower() == 'shap': 
        print("Declare shap functions.... to be imporve")
 

    # to be improve