'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the jason data to ges file
 All rights reserved
'''
import re as regx
import os
from expr import idx_summation
from expr import cmplx_expr
from expr import split_expr
import math

def xde2ges(gesname,coortype,keywd_tag,xde_lists,list_addr,keyws_reg,file):

    # 0 prepare
    shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
    gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
    if gaus_tag != None:
        gaus_tag = gaus_tag.group()
        
    dim = regx.search(r'[1-9]+',coortype,regx.I).group()
    axi = coortype.split('d')[1]
    
    
    file.write(gesname+'\ndefi\n')
    pfelacpath = os.environ['pfelacpath']
    
    code_use_dict = {} # use to deal with @L, @A, vol, singular, ...
    for code_key in ['BFmate','AFmate','func','stif','mass','damp']:
        if code_key in xde_lists['code']:
            code_use_dict[code_key] = []
            release_code(xde_lists,code_key,pfelacpath,code_use_dict)

    #for strs in code_use_dict.keys():
    #    print(code_use_dict[strs])
    
    # 1 write disp and var declare
    # 1.1 parsing var
    var_dict = {}
    if 'disp' in xde_lists:
    
        for shap_type in xde_lists['shap'].keys():
        
            nodn = int(regx.search(r'[1-9]+',shap_type,regx.I).group())
            
            for var in xde_lists['shap'][shap_type]:
                var_dict[var] = []
                for ii in range(nodn):
                    var_dict[var].append(var+str(ii+1))
                
    # 1.2 write disp declare
    if 'disp' in xde_lists:
        file.write('disp ')
        for strs in xde_lists['disp']:
            file.write(strs+',')
        file.write('\n')
        i = 0
        
    # 1.3 write var declare
    nodn = int(regx.search(r'[1-9]+',shap_tag,regx.I).group())
    if 'disp' in xde_lists:
        file.write('var')
        for nodi in range(nodn):
            for strs in xde_lists['disp']:
                if nodi >= len(var_dict[strs]):
                    continue
                file.write(' '+var_dict[strs][nodi])
                i += 1
                if i == 10:
                    file.write('\nvar')
                    i = 0    
        file.write('\n')
        
    # 2 write refc and coor declare
    if 'coor' in xde_lists:
        file.write('refc ')
        for strs in xde_lists['coor']:
            file.write('r'+strs+',')
        file.write('\n')
        file.write('coor ')
        for strs in xde_lists['coor']:
            file.write(strs+',')
        file.write('\n')
    
    # 3 write func declare
    if 'func' in xde_lists:
        file.write('func = ')
        for strs in xde_lists['func']:
            file.write(strs+',')
        file.write('\n')

    # 4 write dord declare
    if 'disp' in xde_lists:
        file.write('dord ')
        for strs in xde_lists['disp']:
            file.write('1'+',')
        file.write('\n')
        
    # 5 write code before mate declaration
    if 'BFmate' in code_use_dict:
        for strs in code_use_dict['BFmate']:
            file.write(strs)
    
    # 6 write mate line
    if 'mate' in xde_lists:
        file.write('mate')
        for var in xde_lists['mate']['default'].keys():
            file.write(' '+var)
        for var in xde_lists['mate']['default'].keys():
            file.write(' '+xde_lists['mate']['default'][var])
        file.write('\n')
        
    # 7 write code after mate declaration
    if 'AFmate' in code_use_dict:
        for strs in code_use_dict['AFmate']:
            file.write(strs)
    
    # 8 write 'singular' operator declaration
    if 'singular' in xde_lists:
        file.write(xde_lists['singular'])
    
    # 9 write shap and tran paragraph
    file.write('\nshap\n')
    if 'shap' in xde_lists:
        geslib_coor = ['x','y','z']
        main_shap_string = ''
        
        # 9.1 write shap
        for shap_type in xde_lists['shap'].keys():
            
            shap_func = 'd'+dim+shap_type+'.sub'
            path_shap = pfelacpath+'ges/ges.lib'
            file_shap = open(path_shap, mode='r')
            shap_find = 0
            shap_string = ''
            
            # 9.1.1 find shap function in ges.lib
            for line in file_shap.readlines():
                shap_start_file = regx.search('sub '+shap_func,line,regx.I)
                shap_end_file   = regx.search('end '+shap_func,line,regx.I)
                if shap_start_file != None:
                    shap_find = 1
                    continue
                if shap_end_file   != None:
                    shap_find = 0
                    continue
                if shap_find == 1:
                    shap_string+=line
            file_shap.close()
            
            # note: save the main shap function for mix element when write tran
            if shap_type == shap_tag:
                main_shap_string = shap_string
            
            # 9.1.2 replace shap func's coor by xde's coor
            coor_i = 0
            for strs in xde_lists['coor']:
                shap_string = shap_string.replace(geslib_coor[coor_i],'r'+strs)
                coor_i += 1
            
            # 9.1.3 replace shap func's disp by xde's disp and write
            for strs in xde_lists['shap'][shap_type]:
                shap_string = shap_string.replace('u',strs)
                
                file.write(strs+'=\n')
                file.write(shap_string)
                file.write('\n')
        
        # 9.2 write tran
        file.write('tran\n')
        trans_list = main_shap_string.split('\n')
        trans_list.remove('')
        tran_list = []
        
        # 9.2.1 add '()'
        for strs in trans_list:
            temp_list = strs.split('=')
            temp_num = regx.search(r'[0-9]+',temp_list[0],regx.I).group()
            temp_list[0] = temp_list[0].replace(temp_num,'('+temp_num+')')
            tran_list.append(temp_list[0]+'='+temp_list[1])
        
        # 9.2.2 replace shap func's disp by by xde's coor and write
        shap_i = 0
        for strs in xde_lists['coor']:
            file.write(strs+'=\n')
            for strss in tran_list:
                file.write(strss.replace('u',strs)+'\n')
            file.write('\n')
            shap_i += 1
            
    # 9 write gaus paragraph
    if 'gaus' in xde_lists:

        # 9.1 Gaussian integral
        if xde_lists['gaus'][0] == 'g':
        
            gaus_degree = regx.search(r'[0-9]+',xde_lists['gaus'],regx.I).group()
        
            # 9.1.1 line square or cube shap
            if shap_tag[0].lower()=='l' \
            or shap_tag[0].lower()=='q' \
            or shap_tag[0].lower()=='c':
            
                path_gaus = pfelacpath+'ges/gaus.pnt'
                file_gaus = open(path_gaus, mode='r')
                gaus_find = 0
                gaus_axis = []
                gaus_weit = []
                
                # 9.1.1.1 read gaus axis and weight in gaus.pnt
                for line in file_gaus.readlines():
                    gaus_start_file = regx.search('n='+gaus_degree,line,regx.I)
                    if gaus_start_file != None:
                        gaus_find = 1
                        continue
                    if gaus_find == 1 and line=='\n':
                        gaus_find = 0
                        continue
                    if gaus_find == 1:
                        gaus_string = line.split()
                        if gaus_string[0][0] != '-':
                            gaus_string[0] = ' '+gaus_string[0]
                        gaus_axis.append(gaus_string[0])
                        gaus_weit.append(gaus_string[1])
                        
                file_gaus.close()
                
                # 9.1.1.2 write line square or cube's gaussian integra
                file.write('gaus = '+str(len(gaus_weit)**int(dim))+'\n')
                
                if   shap_tag[0].lower()=='l':
                    for axis_i in range(len(gaus_axis)):
                        file.write(gaus_axis[axis_i]+' ' \
                                  +gaus_weit[axis_i]+'\n')
                        
                elif shap_tag[0].lower()=='q':
                    for axis_i in range(len(gaus_axis)):
                        for axis_j in range(len(gaus_axis)):
                            weight = float(gaus_weit[axis_i]) \
                                    *float(gaus_weit[axis_j])
                            file.write(gaus_axis[axis_i]+' ' \
                                      +gaus_axis[axis_j]+' ' \
                                      +str(weight)+'\n')
                                      
                elif shap_tag[0].lower()=='c':
                    for axis_i in range(len(gaus_axis)):
                        for axis_j in range(len(gaus_axis)):
                            for axis_k in range(len(gaus_axis)):
                                weight = float(gaus_weit[axis_i]) \
                                        *float(gaus_weit[axis_j]) \
                                        *float(gaus_weit[axis_k])
                                file.write(gaus_axis[axis_i]+' ' \
                                          +gaus_axis[axis_j]+' ' \
                                          +gaus_axis[axis_k]+' ' \
                                          +str(weight)+'\n')
            
            # 9.1.2 triangle shap
            elif shap_tag[0].lower()=='t':
            
                path_gaus = pfelacpath+'ges/gaust.pnt'
                file_gaus = open(path_gaus, mode='r')
                gaus_find = 0
                gaus_string = ''
                
                # 9.1.2.1 tackle the gaussian degree
                if gaus_degree == '6':
                    gaus_degree = '5'
                elif int(gaus_degree) > 12 and int(gaus_degree) < 17:
                    gaus_degree = '12'
                elif int(gaus_degree) > 17:
                    gaus_degree = 17
                
                # 9.1.2.2 read gaus axis and weight in gaust.pnt and write
                for line in file_gaus.readlines():
                    gaus_start_file = regx.search('P'+gaus_degree,line,regx.I)
                    if gaus_start_file != None:
                        gaus_find = 1
                        continue
                    if gaus_find == 1 and line=='\n':
                        gaus_find = 0
                        continue
                    if gaus_find == 1:
                        gaus_string += line
    
                file_gaus.close()
                file.write(gaus_string)
            
            # 9.1.3  tetrahedron shap    
            elif shap_tag[0].lower()=='w':
            
                path_gaus = pfelacpath+'ges/gausw.pnt'
                file_gaus = open(path_gaus, mode='r')
                gaus_find = 0
                gaus_string = ''
                
                # 9.1.3.1 tackle the gaussian degree
                if gaus_degree == '4':
                    gaus_degree = '3'
                elif gaus_degree == '6':
                    gaus_degree = '5'
                elif int(gaus_degree) > 7:
                    gaus_degree = '7'
                
                # 9.1.2.2 read gaus axis and weight in gausw.pnt and write            
                for line in file_gaus.readlines():
                    gaus_start_file = regx.search('P'+gaus_degree,line,regx.I)
                    if gaus_start_file != None:
                        gaus_find = 1
                        continue
                    if gaus_find == 1 and line=='\n':
                        gaus_find = 0
                        continue
                    if gaus_find == 1:
                        gaus_string += line
    
                file_gaus.close()
                file.write(gaus_string)
                
            else: pass
        
        # 9.2 node integral    
        else:
            path_gaus = pfelacpath+'ges/ges.lib'
            file_gaus = open(path_gaus, mode='r')
            gaus_find = 0
            gaus_string = ''
            
            # 9.2.1 read gaus axis and weight in ges.lib and write
            for line in file_gaus.readlines():
                gaus_start_file = regx.search('sub d'+dim+xde_lists['gaus']+'.gau',line,regx.I)
                gaus_end_file   = regx.search('end d'+dim+xde_lists['gaus']+'.gau',line,regx.I)
                if gaus_start_file != None:
                    gaus_find = 1
                    continue
                if gaus_end_file != None:
                    gaus_find = 0
                    continue
                if gaus_find == 1:
                    gaus_string += line
                    
            file_gaus.close()
            file.write(gaus_string)
        
    
    # 10 write func paragraph
    if 'func' in code_use_dict \
    or 'vol'  in xde_lists :
        file.write('\nfunc\n')
        if 'vol'  in xde_lists :
            file.write(xde_lists['vol'])
        if 'func' in code_use_dict:
            for strs in code_use_dict['func']:
                file.write(strs)
    
    # 11 write stif, mass, damp paragraph
    for weak in ['stif', 'mass', 'damp']:
        if weak in xde_lists:
            file.write('\n{}\n'.format(weak))
            if weak in code_use_dict:
                for strs in code_use_dict[weak]:
                    file.write(strs)
            if xde_lists[weak][0] == 'dist':
                left_var  = xde_lists[weak][0]
                righ_expr = ''
                for ii in range(1,len(xde_lists[weak])):
                    righ_expr += xde_lists[weak][ii]

                expr_list = idx_summation(left_var,righ_expr,xde_lists)
                expr_list = split_expr(expr_list[0])
                for strs in expr_list:
                    if strs == 'dist=':
                        file.write(strs)
                    else:
                        file.write(strs+'\n')
            elif xde_lists[weak][0] == 'lump':
                file.write('lump =\n')
                for shaps in xde_lists['shap']:
                    nodn = regx.search(r'\d+',shaps,regx.I).group()
                    for vara in xde_lists['shap'][shaps]:
                        for ii in range(int(nodn)):
                            file.write('+[{}]{}{}\n'.format(xde_lists[weak][1],vara,ii+1))
        
    # 14 write load paragraph
    file.write('\nload\n')
    if 'load' in xde_lists:
        left_var  = 'load'
        righ_expr = ''
        for strs in xde_lists['load']:
            righ_expr += strs
        expr_list = idx_summation(left_var,righ_expr,xde_lists)
        expr_list = split_expr(expr_list[0])
        for strs in expr_list:
            if strs == 'load=':
                file.write(strs)
            else:
                file.write(strs+'\n')
    else:
        print('error: no load declared')

    file.write('\nend')

    file.close()

    import json
    file = open('../1ges_target/code_use_dict.json',mode='w')
    file.write(json.dumps(code_use_dict,indent=4))
    file.close()

def release_code(xde_lists,code_place,pfelacpath,code_use_dict):
    
    for strs in xde_lists['code'][code_place]:
        
        regxrp = regx.search(r'Insr|Tnsr|Cplx|Oprt|Func',strs,regx.I)

        if regxrp == None:
            code_use_dict[code_place].append(strs+'\n')
        else:
        
            # Insert C code
            if   regxrp.group() == 'Insr':
                code_use_dict[code_place].append(strs.replace('Insr_C:','$cc')+'\n')
            
            # Tensor expr summation
            elif regxrp.group() == 'Tnsr':
            
                vector_expr = strs.replace('Tnsr_Asgn: ','')
                left_var  = vector_expr.split('=')[0].strip()
                righ_expr = vector_expr.split('=')[1].strip()
    
                expr_list = idx_summation(left_var,righ_expr,xde_lists)
                for exprs in expr_list:
                    code_use_dict[code_place].append('$cc '+exprs+';\n')
    
            # complex expr expansion    
            elif regxrp.group() == 'Cplx':
                complex_expr = strs.replace('Cplx_Asgn: ','')
                left_var  = complex_expr.split('=')[0].strip()
                righ_expr = complex_expr.split('=')[1].strip()
    
                # if complex expr is a tensor expr, make summation first
                if left_var .find('_') != -1 \
                or righ_expr.find('_') != -1 :
                    expr_list = idx_summation(left_var,righ_expr,xde_lists)
                    for exprs in expr_list:
                        cmplx_list = exprs.split('=')
                        aa = cmplx_expr(cmplx_list[1])
                        for ri,cmplexpr in zip(['r','i'],aa.complex_list):
                            code_use_dict[code_place].append('$cc {}{}={}\n'.format(cmplx_list[0],ri,cmplexpr))
                else:
                    bb = cmplx_expr(righ_expr)
                    i = 0
                    for ri,cmplexpr in zip(['r','i'],bb.complex_list):
                        code_use_dict[code_place].append('$cc {}{}={}\n'.format(left_var,ri,cmplexpr))
                    i += 1
    
            # the operator resault assignment
            elif regxrp.group() == 'Oprt':
                path_oprt = pfelacpath+'ges/pde.lib'
                file_oprt = open(path_oprt, mode='r')
                oprt_expr = strs.replace('Oprt_Asgn: ','')
                
                # singularity and volume operators
                for oprt_key in ['singular','vol']:
                    if oprt_expr.find(oprt_key) != -1:
                        oprt_strs = ''
                        oprt_find = 0
    
                        for line in file_oprt.readlines():
                            oprt_start_file = regx.match('sub '+oprt_expr+'\(',line,regx.I)
                            oprt_end_file   = regx.match('end '+oprt_expr,line,regx.I)
                            if oprt_start_file != None:
                                oprt_find = 1
                                continue
                            if oprt_end_file   != None:
                                oprt_find = 0
                                continue
                            if oprt_find == 1:
                                oprt_strs+=line
    
                        xde_lists[oprt_key] = oprt_strs
    
                # other operators as grad, div, curl...
                if  oprt_expr.find('singular') == -1 \
                and oprt_expr.find('vol') == -1 :
    
                    # split aa=grad.xy(x,y,u) to aa, grad.xy, [x,y,u]
                    left_var  = oprt_expr.split('=')[0]
                    righ_expr = oprt_expr.split('=')[1]
                    oprt_name = righ_expr.split('(')[0]
                    oprt_vars = righ_expr.split('(')[1].rstrip(')').split(',')
                    temp_vars = []
    
                    # expand vector variable list [x_i,a_i...] --> [x,y,z,a1,a2,...]
                    for vara in oprt_vars:
                        if vara.count('_') == 0:
                            temp_vars.append(vara)
                        elif vara.count('_') == 1:
                            vect_var = vara.split('_')[0]
                            temp_vars += xde_lists['vect'][vect_var]
                        elif vara.count('_') == 2:
                            matr_var = vara.split('_')[0]
                            for matr_row in xde_lists['matrix'][matr_var]:
                                temp_vars += matr_row
                    oprt_vars = temp_vars.copy()
    
                    oprt_strs = ''
                    oprt_find = 0
                    # find operator in pde.lib
                    for line in file_oprt.readlines():
                        oprt_start_file = regx.search('sub '+oprt_name+'\(',line,regx.I)
                        oprt_end_file   = regx.search('end '+oprt_name,line,regx.I)
                        if oprt_start_file != None:
                            oprt_find = 1
                            temp_vars = line.split('(')[1].rstrip().rstrip(')').split(',').copy()
                            continue
                        if oprt_end_file   != None:
                            oprt_find = 0
                            continue
                        if oprt_find == 1:
                            oprt_strs+=line

                    # replace default variable by operator variable
                    if len(oprt_vars) == len(temp_vars):
                        for oprt_var, temp_var in zip(oprt_vars, temp_vars):
                            oprt_strs = oprt_strs.replace(temp_var,oprt_var)

                    # assign to a temporary list type of 'fvect' or 'fmatr' 
                    # used for derivative of 'disp' variables in Func_Asgn step
                    if  left_var[0]  == '[' \
                    and left_var[-1] == ']' :
                        oprt_list = oprt_strs.rstrip().split('\n')
                        if left_var.count('_') == 0:
                            oprt_expr = left_var.lstrip('[').rstrip(']')+'='
                            for vara in oprt_list:
                                oprt_expr += vara
                            code_use_dict[code_place].append(oprt_expr)
                        elif left_var.count('_') == 1:
                            oprt_expr = left_var.lstrip('[').rstrip(']').split('_')[0]
                            for vara in oprt_list:
                                xde_lists['fvect'][oprt_expr].append(vara)
    
                        elif left_var.count('_') == 2:
                            oprt_expr = left_var.lstrip('[').rstrip(']').split('_')[0]
                            row = int(xde_lists['fmatr'][oprt_expr][0])
                            clm = int(xde_lists['fmatr'][oprt_expr][1])
                            for iii in range(row):
                                xde_lists['fmatr'][oprt_expr].append([])
                                for jjj in range(clm):
                                    xde_lists['fmatr'][oprt_expr][iii+2].append(oprt_list[iii*row+jjj])
    
                    # assign to derivative of distributed known variables such as last step 'disp' resault
                    elif left_var[0]  != '[' \
                    and  left_var[-1] != ']' :
                        oprt_strs = oprt_strs.replace('[','{').replace(']','}')
                        oprt_list = oprt_strs.rstrip().split('\n')
                        if left_var.count('_') == 0:
                            oprt_expr = left_var.lstrip('[').rstrip(']')+'='
                            for vara in oprt_list:
                                oprt_expr += vara
                            code_use_dict[code_place].append(oprt_expr)
                        elif left_var.count('_') == 1:
                            oprt_expr = left_var.lstrip('[').rstrip(']').split('_')[0]
                            if len(xde_lists['vect'][oprt_expr]) == len(oprt_list):
                                for iii in range(len(oprt_list)):
                                    code_use_dict[code_place].append(xde_lists['vect'][oprt_expr][iii]+'='+oprt_list[iii])
                        elif left_var.count('_') == 2:
                            oprt_expr = left_var.lstrip('[').rstrip(']').split('_')[0]
                            matr_len = 0
                            for lists in xde_lists['matrix'][oprt_expr]:
                                matr_len += len(lists)
                            if matr_len == len(oprt_list):
                                iii = 0
                                for lists in xde_lists['matrix'][oprt_expr]:
                                    for strss in lists:
                                        code_use_dict[code_place].append('$cv '+strss+'='+oprt_list[iii]+'\n')
                                        iii += 1
                file_oprt.close()
    
            elif regxrp.group() == 'Func':
                left_var  = strs.split(' ')[1].split('=')[0]
                righ_expr = strs.split(' ')[1].split('=')[1]
    
                # assign the temporary list type of 'fvect' or 'fmatr'
                # to the list type of 'vect' or 'matrix'
                if  left_var[0]  != '[' \
                and left_var[-1] != ']' :
                    if regx.search(r'[a-z]+[0-9a-z]*\[([0-9],)*[0-9]?\]',righ_expr,regx.I) != None \
                    and righ_expr[-1] == ']':
                        print(righ_expr)
    
                        righ_var = righ_expr.split('[')[0]
                        righ_idx = righ_expr.split('[')[1].rstrip(']').split(',')
    
                        if left_var.count('_') == 0:
                            oprt_expr = left_var+'='
    
                            if 'fvect' in xde_lists \
                            and righ_var in xde_lists['fvect']:
                                for idx in righ_idx:
                                    oprt_expr += xde_lists['fvect'][righ_var][int(idx)]
    
                            elif 'fmatr' in xde_lists \
                            and righ_var in xde_lists['fmatr']:
    
                                row = int(xde_lists['fmatr'][righ_var][0])
                                clm = int(xde_lists['fmatr'][righ_var][1])
                                fmatr = xde_lists['fmatr'][righ_var][2:len(xde_lists['fmatr'][righ_var])]
    
                                for idx in righ_idx:
                                    oprt_expr += fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1]
    
                            code_use_dict[code_place].append(oprt_expr+'\n\n')
    
                        elif left_var.count('_') == 1: 
                            left_vara_name = left_var.split('_')[0]
                            oprt_expr_list = []
    
                            if len(xde_lists['vect'][left_vara_name]) == len(righ_idx):
                                if 'fvect' in xde_lists \
                                and righ_var in xde_lists['fvect']:
                                    for vara,idx in zip(xde_lists['vect'][left_vara_name],righ_idx):
                                        oprt_expr_list.append(vara+'='+xde_lists['fvect'][righ_var][int(idx)]+'\n\n')
    
                                elif 'fmatr' in xde_lists \
                                and righ_var in xde_lists['fmatr']:
                                    row = int(xde_lists['fmatr'][righ_var][0])
                                    clm = int(xde_lists['fmatr'][righ_var][1])
                                    fmatr = xde_lists['fmatr'][righ_var][2:len(xde_lists['fmatr'][righ_var])]
                                    for vara,idx in zip(xde_lists['vect'][left_vara_name],righ_idx):
                                        oprt_expr_list.append(vara+'='+fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1]+'\n\n')
    
                            code_use_dict[code_place] += oprt_expr_list
    
                        elif left_var.count('_') == 2:
                            left_vara_name = left_var.split('_')[0]
                            oprt_expr_list = []
                            matr_len = 0
                            for lists in xde_lists['matrix'][left_vara_name]:
                                matr_len += len(lists)
    
                            if matr_len == len(righ_idx):
                                if 'fvect' in xde_lists \
                                and righ_var in xde_lists['fvect']:
                                    idx = 0
                                    for lists in xde_lists['matrix'][left_vara_name]:
                                        for vara in lists:
                                            idx+=1
                                            oprt_expr_list.append(vara+'='+xde_lists['fvect'][righ_var][idx]+'\n\n')
    
                                elif 'fmatr' in xde_lists \
                                and righ_var in xde_lists['fmatr']:
                                    fmatr = xde_lists['fmatr'][righ_var][2:len(xde_lists['fmatr'][righ_var])]
                                    i = 0
                                    for matr_row in xde_lists['matrix'][left_vara_name]:
                                        for matr_vara in matr_row:
                                            idx = righ_idx[i]
                                            oprt_expr_list.append(matr_vara+'='+fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1]+'\n\n')
                                            i += 1
    
                            code_use_dict[code_place] += oprt_expr_list
    
                # assign the temporary list type of 'fvect' or 'fmatr'
                # to the list type of 'fvect' or 'fmatr'
                elif left_var[0]  == '[' \
                and  left_var[-1] == ']' : 
                    vector_expr = strs.replace('Func_Asgn: ','').replace('[','').replace(']','')
                    left_var  = vector_expr.split('=')[0].strip()
                    righ_expr = vector_expr.split('=')[1].strip()
                    expr_list = idx_summation(left_var,righ_expr,xde_lists)
    
                    if left_var.count('_') == 1:
                        left_var = left_var.split('_')[0]
                        for ii in range(1,len(xde_lists['fvect'][left_var])):
                            xde_lists['fvect'][left_var][ii] \
                                = expr_list[ii-1].split('=')[1].replace('++','+').replace('-+','-')
                    elif left_var.count('_') == 2:
                        left_var = left_var.split('_')[0]
                        for ii in range(2,len(xde_lists['fmatr'][left_var])):
                            for jj in range(len(xde_lists['fmatr'][left_var][2])):
                                xde_lists['fmatr'][left_var][ii][jj] \
                                    = expr_list[ii-2+jj].split('=')[1].replace('++','+').replace('-+','-')

