'''
 Copyright: Copyright (c) 2019
 Created: 2019-7-12
 Author: Zhang_Licheng
 Title: parse xde file to html file
 All rights reserved
'''
import re
import os
from expr import split_bracket_expr

def xde2html(ges_info, xde_dict, xde_addr, file):
    pfelacpath = os.environ["pfelacpath"].replace("\\","/")

    file.write("<!DOCTYPE html>\n")
    file.write("<html>\n")
    file.write("<head>\n")
    file.write("<title>Preview</title>\n")
    file.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n')
    file.write(f'<script type="text/javascript" src="{pfelacpath}MathJax-master/MathJax.js?config=TeX-AMS-MML_HTMLorMML.js"></script>\n')
    file.write("</head>\n")
    file.write("<body>\n")
    
    # 1 write disp
    if 'disp' in xde_dict:
        file.write('<blockquote>\n')
        file.write('<h3>Unknown Variable, \'Disp\':</h3>\n')
        file.write('<p>\n')
        for var in xde_dict['disp']:
            file.write(var+', ')
        file.write('\n')
        file.write('</p>\n')
        file.write('</blockquote>\n')

    # 2 write coef
    if 'coef' in xde_dict:
        file.write('<blockquote>\n')
        file.write('<h3>Coupled Variable, \'Coef\':</h3>\n')
        file.write('<p>\n')
        for var in xde_dict['coef']:
            file.write(var+', ')
        file.write('\n')
        file.write('</p>\n')
        file.write('</blockquote>\n')

    # 3 write coor
    if 'coor' in xde_dict:
        coortype = f"{ges_info['dim']}d{ges_info['axi']}"
        file.write('<blockquote>\n')
        file.write(f'<h3>Coordinate Type, \'Coor\': {coortype}</h3>\n')
        file.write('<p>\n')
        for var in xde_dict['coor']:
            file.write(var+', ')
        file.write('\n')
        file.write('</p>\n')
        file.write('</blockquote>\n')

    # 4 write default material
    if 'mate' in xde_dict:
        file.write('<blockquote>\n')
        file.write(f'<h3>Default Material, \'Mate\':</h3>\n')
        file.write(f'<table border="1" cellpadding="10" cellspacing="0">\n')
        table_style = 'cross'
        if table_style == 'vertical':
            file.write('\t<tr>\n')
            file.write('\t\t<td>var</td>\n')
            file.write('\t\t<td>val</td>\n')
            file.write('\t</tr>\n')
            for var, val in xde_dict['mate']['default'].items():
                file.write('\t<tr>\n')
                file.write(f'\t\t<td>{var}</td>\n')
                file.write(f'\t\t<td>{val}</td>\n')
                file.write('\t</tr>\n')
        elif table_style == 'cross':
            file.write('\t<tr>\n')
            file.write('\t\t<td>var</td>\n')
            for var in xde_dict['mate']['default'].keys():
                file.write(f'\t\t<td>{var}</td>\n')
            file.write('\t</tr>\n')
            file.write('\t<tr>\n')
            file.write('\t\t<td>val</td>\n')
            for val in xde_dict['mate']['default'].values():
                file.write(f'\t\t<td>{val}</td>\n')
            file.write('\t</tr>\n')
        file.write('</table>\n')
        file.write('</blockquote>\n')

    # 5 write shap
    if 'shap' in xde_dict:
        for shap_var in ['shap','coef_shap']:
            if shap_var in xde_dict:
                file.write('<blockquote>\n')
                file.write(f'<h3>Element Type, \'{shap_var}\':</h3>\n')
                for shap_i, key_var in enumerate(xde_dict[shap_var].keys()):
                    file.write('<p>\n')
                    file.write('\tType {}: {}, '.format(shap_i+1,key_var))
                    if key_var == 'l2':
                        file.write('First Order Linear Element<br>\n')
                    elif key_var == 'l3':
                        file.write('Second Order Linear Element<br>\n')
                    elif key_var == 't3':
                        file.write('First Order Triangle Element<br>\n')
                    elif key_var == 't6':
                        file.write('Second Order Triangle Element<br>\n')
                    elif key_var == 'q4':
                        file.write('First Order Quadrilateral Element<br>\n')
                    elif key_var == 'q9':
                        file.write('Second Order Quadrilateral Element<br>\n')
                    elif key_var == 'w4':
                        file.write('First Order Tetrahedral Element<br>\n')
                    elif key_var == 'w10':
                        file.write('Second Order Tetrahedral Element<br>\n')
                    elif key_var == 'c8':
                        file.write('First Order Hexahedral Element<br>\n')
                    elif key_var == 'c27':
                        file.write('Second Order Hexahedral Element<br>\n')
                    else: pass # need to expand
                    file.write(f'\t{"&nbsp "*6}Applicable to: ')
                    for var in xde_dict[shap_var][key_var]:
                        file.write(var+', ')
                    file.write('\n')
                    file.write('</p>\n')

                file.write('</blockquote>\n')

    # 6 write gaus
    if 'gaus' in xde_dict:
        file.write('<blockquote>\n')
        file.write(f'<h3>Element Integration Type, {xde_dict["gaus"]}:</h3>\n')
        file.write('<p>\n')
        if xde_dict['gaus'][0] == 'g':
            file.write('Gaussian integral grade {}\n'.format(xde_dict['gaus'].replace('g','')))
        else:
            file.write('element node integral\n')
        file.write('</p>\n')
        file.write('</blockquote>\n')
        
    # 7 write mass damp
    for strs in ['mass','damp']:
        if strs in xde_dict:

            if strs == 'mass':
                if 'damp' in xde_dict:
                    order = 'Second'
                    ordei = '^2'
                else:
                    order = 'First'
                    ordei = ''
            else:
                order = 'First'
                ordei = ''

            file.write('<blockquote>\n')
            file.write('<h3>{0} items ({1} Order Time Derivative), \'{0}\':</h3>\n'.format(strs,order))
            file.write('<p>\n')
            if xde_dict[strs][0] == 'lump':
                file.write('\tLumped {} Matrix:\n'.format(strs))
                file.write('\\[\n')
                write_line = ''
                for var in xde_dict['disp']:
                    write_line += ' \\int_{\Omega} '
                    write_line += xde_dict[strs][1].replace('*','\cdot ')+'\cdot '
                    write_line += '\\frac{\\partial'
                    write_line += ordei+' '
                    write_line += var
                    write_line += '}{\\partial t'
                    write_line += ordei+'}\delta '
                    write_line += var
                    write_line += ' +'
                write_line = write_line.rstrip('+')
                file.write(write_line)
                file.write('\n\\]\n')
            elif xde_dict[strs][0] == 'dist':
                dist_weak(strs, xde_dict, file)
            file.write('</p>\n')
            file.write('</blockquote>\n')

    # 8 write stif
    if 'stif' in xde_dict:
        if xde_dict['stif'][0] == 'dist':
            file.write('<blockquote>\n')
            file.write('<h3>Stiffness items, \'stif\':</h3>\n')
            file.write('<p>\n')
            file.write('\t Distribute Stiffness Matrix:\n')
            dist_weak('stif', xde_dict, file)
            file.write('</p>\n')
            file.write('</blockquote>\n')

    file.write("</body>\n")
    file.write("</html>\n")
        
def dist_weak(weaktype, xde_dict, file):
    file.write('\\[\n')
    write_line = ''
    expr_list = []
    for ii in range(1,len(xde_dict[weaktype])):
        expr_list += split_bracket_expr(xde_dict[weaktype][ii])
    
    for weak_strs in expr_list:

        def tran_index(matched):
            index_str = matched.group('index')
            index_list = index_str.split('_')
            index_str = '_{'
            for jj in range(0,len(index_list)):
                index_str += index_list[jj]
            index_str+='}'
            return index_str

        weak_strs = re.sub(r'(?P<index>(_[a-z])+)',tran_index,weak_strs)

        weak_list = []
        second_opr = ''
        first_opr = ''
        factor = ''

        if weak_strs[0] != '[':
            first_opr = weak_strs[0]
        else:
            first_opr = '+'
        weak_strs = weak_strs.split('[')[1]

        weak_list = weak_strs.split(';')
        if weaktype == 'mass':
            if 'damp' in xde_dict:
                left = '\\frac{\\partial^2 '+ weak_list[0] + '}{\\partial t^2}'
            else:
                left = '\\frac{\\partial '  + weak_list[0] + '}{\\partial t}'
        elif weaktype == 'damp':
            left = '\\frac{\\partial '  + weak_list[0] + '}{\\partial t}'
        elif weaktype == 'stif':
            left = weak_list[0]

        weak_strs = weak_list[1]

        weak_list = weak_strs.split(']')
        righ = weak_list[0]
        weak_strs = weak_list[1]

        if weak_strs == '':
            factor = ''
        else:
            if weak_strs[0] == '/':
                second_opr = '/'
            factor = weak_strs.lstrip(weak_strs[0])
            if second_opr == '/':
                factor = '1/'+factor

        write_line += ' \\int_{\Omega} '
        write_line += factor.rstrip('+').replace('*','\cdot ')+'\cdot '
        write_line += left
        write_line += '\delta '+righ
        write_line += '+'

    write_line = write_line.rstrip('+')
    file.write(write_line)
    file.write('\n\\]\n')