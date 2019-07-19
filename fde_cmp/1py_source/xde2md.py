'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-26
 Author: Zhang_Licheng
 Title: parse xde file to markdown file
 All rights reserved
'''
import re as regx
import os

def xde2md(gesname,coortype,xde_dict,xde_addr,file):

    # 0 prepare
    shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
    gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
    if gaus_tag != None:
        gaus_tag = gaus_tag.group()

    dim = regx.search(r'[1-9]+',coortype,regx.I).group()
    axi = coortype.split('d')[1]

    # 1 write disp
    if 'disp' in xde_dict:

        file.write('#### Unknown Variable, \'Disp\':\n\t')
        for var in xde_dict['disp']:
            file.write(var+', ')
        file.write('\n')

    # 2 write coef
    if 'coef' in xde_dict:

        file.write('#### Coupled Variable, \'Coef\':\n\t')
        for var in xde_dict['coef']:
            file.write(var+', ')
        file.write('\n')


    # 3 write coor
    if 'coor' in xde_dict:

        file.write('#### Coordinate Type, \'Coor\': {}\n\t'.format(coortype))
        for var in xde_dict['coor']:
            file.write(var+', ')
        file.write('\n')

    # 4 write default material
    if 'mate' in xde_dict:

        file.write('#### Default Material, \'Mate\':\n')
        file.write('| var|value|\n')
        file.write('|:---:|:---:|\n')
        for var in xde_dict['mate']['default'].keys():
            file.write('|'+var+'|'+xde_dict['mate']['default'][var]+'|\n')

    # 5 write shap
    if 'shap' in xde_dict:

        for shap_var in ['shap','coef_shap']:
            if shap_var in xde_dict:
                file.write('#### Element Type, \'{}\':\n'.format(shap_var))
                shap_i = 0
                for key_var in xde_dict[shap_var].keys():
                    shap_i += 1
                    file.write('\tType {}: {}, '.format(shap_i,key_var))
                    if key_var == 'l2':
                        file.write('First Order Linear Element\n')
                    elif key_var == 'l3':
                        file.write('Second Order Linear Element\n')
                    elif key_var == 't3':
                        file.write('First Order Triangle Element\n')
                    elif key_var == 't6':
                        file.write('Second Order Triangle Element\n')
                    elif key_var == 'q4':
                        file.write('First Order Quadrilateral Element\n')
                    elif key_var == 'q9':
                        file.write('Second Order Quadrilateral Element\n')
                    elif key_var == 'w4':
                        file.write('First Order Tetrahedral Element\n')
                    elif key_var == 'w10':
                        file.write('Second Order Tetrahedral Element\n')
                    elif key_var == 'c8':
                        file.write('First Order Hexahedral Element\n')
                    elif key_var == 'c27':
                        file.write('Second Order Hexahedral Element\n')
                    else: pass # need to expand
                    file.write('\t\tApplicable to: ')
                    for var in xde_dict[shap_var][key_var]:
                        file.write(var+', ')
                    file.write('\n')

    # 6 write gaus
    if 'gaus' in xde_dict:
        file.write('#### Element Integration Type, {}:\n\t'.format(xde_dict['gaus']))

        if xde_dict['gaus'][0] == 'g':
            file.write('Gaussian integral grade {}\n'.format(xde_dict['gaus'].replace('g','')))
        else:
            file.write('element node integral\n')

    # 7 write mass damp
    for strs in ['mass','damp']:
        if strs in xde_dict:

            if strs == 'mass':
                order = 'Second'
                ordei = '^2'
            else:
                order = 'First'
                ordei = ''

            file.write('#### {0} items ({1} Order Time Derivative), \'{0}\':\n'.format(strs,order))
            if xde_dict[strs][0] == 'lump':
                file.write('\tLumped {} Matrix:\n'.format(strs))
                file.write('$$')
                write_line = ''
                for var in xde_dict['disp']:
                    write_line += ' \\int_{\Omega} '
                    write_line += xde_dict[strs][1]+'*'
                    write_line += '\\frac{\\partial'
                    write_line += ordei+' '
                    write_line += var
                    write_line += '}{\\partial t'
                    write_line += ordei+'}\delta '
                    write_line += var
                    write_line += ' +'
                write_line = write_line.rstrip('+')
                file.write(write_line)
                file.write('$$\n')
            elif xde_dict[strs][0] == 'dist': pass

    # 8 write stif
    if 'stif' in xde_dict:
        if xde_dict['stif'][0] == 'dist':

            file.write('#### Stiffness items, \'stif\'\n')
            file.write('\t Distribute Stiffness Matrix:\n')
            file.write('$$')
            write_line = ''

            for ii in range(1,len(xde_dict['stif'])):
                weak_strs = xde_dict['stif'][ii]

                def tran_index(matched):
                    index_str = matched.group('index')
                    index_list = index_str.split('_')
                    index_str = '_{'
                    for jj in range(0,len(index_list)):
                        index_str += index_list[jj]
                    index_str+='}'
                    return index_str

                weak_strs = regx.sub(r'(?P<index>(_[a-z])+)',tran_index,weak_strs)

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
                write_line += factor+'*'
                write_line += left
                write_line += '\delta '+righ
                write_line += '+'

            write_line = write_line.rstrip('+')
            file.write(write_line)
            file.write('$$\n')
            